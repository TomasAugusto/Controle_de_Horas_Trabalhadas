from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta

registrar_horas_bp = Blueprint('registrar_horas', __name__)


#---------------------------------- Registro de Horas-------------------------------------------

# Rota para Registrar Horas
@registrar_horas_bp.route('/registrar_horas', methods=['GET'])
def registrar_horas():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados necessários
    cursor.execute("SELECT IdCliente, Nome FROM Clientes WHERE Ativo = 1")
    clientes = cursor.fetchall()

    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes WHERE Ativo = 1")
    pcos = cursor.fetchall()

    cursor.execute("SELECT IdServico, Nome FROM Servicos WHERE Ativo = 1")
    servicos = cursor.fetchall()

    cursor.execute("SELECT IdTipoHora, Nome FROM TiposHoras WHERE Ativo = 1")
    tipos_horas = cursor.fetchall()

    cursor.execute("SELECT IdAtividade, Nome FROM Atividades WHERE Ativo = 1")
    atividades = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template(
        'registrar_horas.html',
        clientes=clientes,
        pcos=pcos,
        servicos=servicos,
        tipos_horas=tipos_horas,
        atividades=atividades
    )


@registrar_horas_bp.route('/salvar_registro', methods=['POST'])
def salvar_registro():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    data = request.form['data']
    hora_inicio = request.form['hora_inicio']
    hora_fim = request.form['hora_fim']
    id_cliente = request.form['cliente']
    id_pco = request.form['pco']
    id_servico = request.form['servico']
    id_tipo_hora = request.form['tipo_hora']
    id_atividade = request.form['atividade']
    descricao = request.form['descricao']

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o registro na tabela RegistrosHoras
    query = """
    INSERT INTO RegistrosHoras (
        IdColaborador, DataRegistro, HoraInicio, HoraFim, IdCliente, IdPcoCliente, IdServico, IdTipoHora, IdAtividade, Descricao
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        session['usuario_id'], data, hora_inicio, hora_fim, id_cliente, id_pco, id_servico, id_tipo_hora, id_atividade, descricao
    ))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Registro salvo com sucesso!', 'success')
    return redirect(url_for('registrar_horas.registrar_horas'))
    

@registrar_horas_bp.route('/pcos_por_cliente/<int:id_cliente>', methods=['GET'])
def pcos_por_cliente(id_cliente):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os PCOs do cliente selecionado
    cursor.execute("SELECT IdPcoCliente, Nome FROM PcoClientes WHERE IdCliente = ? AND Ativo = 1", (id_cliente,))
    pcos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Retorna os PCOs como JSON
    return jsonify([{'IdPcoCliente': pco.IdPcoCliente, 'Nome': pco.Nome} for pco in pcos])
