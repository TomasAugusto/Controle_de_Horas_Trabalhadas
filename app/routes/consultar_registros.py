from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta
from flask import make_response
from openpyxl import Workbook
from io import BytesIO


consultar_registros_bp = Blueprint('consultar_registros', __name__)


#---------------------------------- Consultar Registros-------------------------------------------

@consultar_registros_bp.route('/consultar_registros')
def consultar_registros():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Verificar se é uma solicitação de exportação
    export = request.args.get('export') == 'excel'
    
    # Obter parâmetros de filtro da query string
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    cliente_id = request.args.get('cliente')
    pco_id = request.args.get('pco')

    # Definir valores padrão para as datas
    hoje = datetime.today()
    primeiro_dia_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    hoje_str = hoje.strftime('%Y-%m-%d')

    # Se não houver filtros, usar os valores padrão
    if not data_inicio:
        data_inicio = primeiro_dia_mes
    if not data_fim:
        data_fim = hoje_str

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta base
    query = """
    SELECT 
        rh.IdRegistroHora,
        rh.DataRegistro,
        rh.HoraInicio,
        rh.HoraFim,
        c.Nome AS Cliente,
        pc.Nome AS PcoCliente,
        s.Nome AS Servico,
        a.Nome AS Atividade,
        th.Nome AS TipoHora,
        rh.Descricao
    FROM RegistrosHoras rh
    INNER JOIN Clientes c ON rh.IdCliente = c.IdCliente
    INNER JOIN PcoClientes pc ON rh.IdPcoCliente = pc.IdPcoCliente
    INNER JOIN Servicos s ON rh.IdServico = s.IdServico
    INNER JOIN Atividades a ON rh.IdAtividade = a.IdAtividade
    INNER JOIN TiposHoras th ON rh.IdTipoHora = th.IdTipoHora
    WHERE rh.IdColaborador = ?
    """

    # Parâmetros da consulta
    params = [session['usuario_id']]

    # Aplicar filtros
    if data_inicio:
        query += " AND rh.DataRegistro >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND rh.DataRegistro <= ?"
        params.append(data_fim)
    if cliente_id:
        query += " AND rh.IdCliente = ?"
        params.append(cliente_id)
    if pco_id:
        query += " AND rh.IdPcoCliente = ?"
        params.append(pco_id)

    query += " ORDER BY rh.DataRegistro DESC"

    # Executar a consulta
    cursor.execute(query, tuple(params))
    registros = cursor.fetchall()

    # Consultar clientes e PCOs para os filtros
    cursor.execute("SELECT IdCliente, Nome FROM Clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes")
    pcos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Se for uma solicitação de exportação para Excel
    if export:
        # Criar um arquivo Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Registros de Horas"

        # Adicionar cabeçalhos
        headers = [
            "Data", "Hora Início", "Hora Fim", "Cliente", "PCO", 
            "Serviço", "Atividade", "Tipo de Hora", "Descrição"
        ]
        ws.append(headers)

        # Adicionar dados
        for registro in registros:
            ws.append([
                registro.DataRegistro.strftime('%d/%m/%Y'),
                registro.HoraInicio,
                registro.HoraFim,
                registro.Cliente,
                registro.PcoCliente,
                registro.Servico,
                registro.Atividade,
                registro.TipoHora,
                registro.Descricao
            ])

        # Ajustar largura das colunas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Criar resposta
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Criar nome do arquivo com data e filtros
        filename = f"registros_horas_{data_inicio}_a_{data_fim}"
        if cliente_id:
            cliente_nome = next((c.Nome for c in clientes if str(c.IdCliente) == cliente_id), "")
            filename += f"_{cliente_nome}"
        filename += ".xlsx"

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response

    # Renderização normal da página
    return render_template(
        'consultar_registros.html',
        registros=registros,
        clientes=clientes,
        pcos=pcos,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@consultar_registros_bp.route('/admin/consultar_registros')
def admin_consultar_registros():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Verificar se é uma solicitação de exportação
    export = request.args.get('export') == 'excel'
    
    # Obter parâmetros de filtro da query string
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    cliente_id = request.args.get('cliente')
    pco_id = request.args.get('pco')
    colaborador_id = request.args.get('colaborador')

    # Definir valores padrão para as datas
    hoje = datetime.today()
    primeiro_dia_mes = hoje.replace(day=1).strftime('%Y-%m-%d')
    hoje_str = hoje.strftime('%Y-%m-%d')

    # Se não houver filtros, usar os valores padrão
    if not data_inicio:
        data_inicio = primeiro_dia_mes
    if not data_fim:
        data_fim = hoje_str

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta base para administradores
    query = """
    SELECT 
        rh.IdRegistroHora,
        rh.DataRegistro,
        rh.HoraInicio,
        rh.HoraFim,
        c.Nome AS Cliente,
        pc.Nome AS PcoCliente,
        s.Nome AS Servico,
        a.Nome AS Atividade,
        th.Nome AS TipoHora,
        rh.Descricao,
        u.Usuario AS Colaborador
    FROM RegistrosHoras rh
    INNER JOIN Clientes c ON rh.IdCliente = c.IdCliente
    INNER JOIN PcoClientes pc ON rh.IdPcoCliente = pc.IdPcoCliente
    INNER JOIN Servicos s ON rh.IdServico = s.IdServico
    INNER JOIN Atividades a ON rh.IdAtividade = a.IdAtividade
    INNER JOIN TiposHoras th ON rh.IdTipoHora = th.IdTipoHora
    INNER JOIN Usuarios u ON rh.IdColaborador = u.IdUsuario
    WHERE 1=1
    """

    # Parâmetros da consulta
    params = []

    # Aplicar filtros
    if data_inicio:
        query += " AND rh.DataRegistro >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND rh.DataRegistro <= ?"
        params.append(data_fim)
    if cliente_id:
        query += " AND rh.IdCliente = ?"
        params.append(cliente_id)
    if pco_id:
        query += " AND rh.IdPcoCliente = ?"
        params.append(pco_id)
    if colaborador_id:
        query += " AND rh.IdColaborador = ?"
        params.append(colaborador_id)

    query += " ORDER BY rh.DataRegistro DESC"

    # Executar a consulta
    cursor.execute(query, tuple(params))
    registros = cursor.fetchall()

    # Consultar clientes, PCOs e colaboradores para os filtros
    cursor.execute("SELECT IdCliente, Nome FROM Clientes")
    clientes = cursor.fetchall()

    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes")
    pcos = cursor.fetchall()

    cursor.execute("SELECT IdUsuario, Usuario FROM Usuarios")
    colaboradores = cursor.fetchall()

    cursor.close()
    conn.close()

    # Se for uma solicitação de exportação para Excel
    if export:
        # Criar um arquivo Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Registros de Horas (Admin)"

        # Adicionar cabeçalhos
        headers = [
            "Colaborador", "Data", "Hora Início", "Hora Fim", "Cliente",
            "PCO", "Serviço", "Atividade", "Tipo de Hora", "Descrição"
        ]
        ws.append(headers)

        # Adicionar dados
        for registro in registros:
            ws.append([
                registro.Colaborador,
                registro.DataRegistro.strftime('%d/%m/%Y'),
                registro.HoraInicio,
                registro.HoraFim,
                registro.Cliente,
                registro.PcoCliente,
                registro.Servico,
                registro.Atividade,
                registro.TipoHora,
                registro.Descricao
            ])

        # Ajustar largura das colunas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width

        # Criar resposta
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Criar nome do arquivo com data e filtros
        filename = f"registros_horas_admin_{data_inicio}_a_{data_fim}"
        if cliente_id:
            cliente_nome = next((c.Nome for c in clientes if str(c.IdCliente) == cliente_id), "")
            filename += f"_{cliente_nome}"
        if colaborador_id:
            colaborador_nome = next((c.Usuario for c in colaboradores if str(c.IdUsuario) == colaborador_id), "")
            filename += f"_{colaborador_nome}"
        filename += ".xlsx"

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response

    # Renderização normal da página
    return render_template(
        'admin_consultar_registros.html',
        registros=registros,
        clientes=clientes,
        pcos=pcos,
        colaboradores=colaboradores,
        data_inicio=data_inicio,
        data_fim=data_fim
    )