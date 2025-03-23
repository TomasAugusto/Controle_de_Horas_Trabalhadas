from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta


consultar_registros_bp = Blueprint('consultar_registros', __name__)


#---------------------------------- Consultar Registros-------------------------------------------

@consultar_registros_bp.route('/consultar_registros')
def consultar_registros():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

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

    # Passar os registros e filtros para o template
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
        u.Usuario AS Colaborador  -- Coluna Usuario na tabela Usuarios
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

    cursor.execute("SELECT IdUsuario, Usuario FROM Usuarios")  #Coluna Usuario na tabela Usuarios
    colaboradores = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passar os registros e filtros para o template
    return render_template(
        'admin_consultar_registros.html',
        registros=registros,
        clientes=clientes,
        pcos=pcos,
        colaboradores=colaboradores, 
        data_inicio=data_inicio,
        data_fim=data_fim
    )

