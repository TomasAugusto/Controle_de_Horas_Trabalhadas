from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta

cadastrar_cliente_bp = Blueprint('cadastrar_cliente', __name__)


#----------------------------------Cadastrar Cliente-------------------------------------------



# Rota para Cadastrar Cliente (apenas administradores)
@cadastrar_cliente_bp.route('/cadastrar_cliente', methods=['GET'])
def cadastrar_cliente():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todos os clientes cadastrados
    cursor.execute("SELECT IdCliente, Nome, Descricao, Ativo FROM Clientes")
    clientes = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_cliente.html', clientes=clientes)

@cadastrar_cliente_bp.route('/salvar_cliente', methods=['POST'])
def salvar_cliente():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo cliente na tabela Clientes
    query = """
    INSERT INTO Clientes (
        Nome, Descricao, IdUsuarioCadastro, Ativo
    ) VALUES (?, ?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, session['usuario_id'], ativo))
        conn.commit()
        flash('Cliente cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o cliente: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_cliente.cadastrar_cliente'))

@cadastrar_cliente_bp.route('/editar_cliente/<int:id_cliente>', methods=['GET'])
def editar_cliente(id_cliente):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados do cliente selecionado
    cursor.execute("""
        SELECT IdCliente, Nome, Descricao, Ativo
        FROM Clientes
        WHERE IdCliente = ?
    """, (id_cliente,))
    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    if not cliente:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('cadastrar_cliente.cadastrar_cliente'))

    # Passa os dados para o template
    return render_template('editar_cliente.html', cliente=cliente)


@cadastrar_cliente_bp.route('/salvar_edicao_cliente/<int:id_cliente>', methods=['POST'])
def salvar_edicao_cliente(id_cliente):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o cliente na tabela Clientes
    query = """
    UPDATE Clientes
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdCliente = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_cliente))
        conn.commit()
        flash('Cliente atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o cliente: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_cliente.cadastrar_cliente'))


