from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta

cadastrar_pco_bp = Blueprint('cadastrar_pco', __name__)


#----------------------------------Cadastrar PCO-------------------------------------------


@cadastrar_pco_bp.route('/cadastrar_pco', methods=['GET'])
def cadastrar_pco():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os clientes
    cursor.execute("SELECT IdCliente, Nome FROM Clientes WHERE Ativo = 1")
    clientes = cursor.fetchall()

    # Consulta para obter todos os PCOs cadastrados
    cursor.execute("""
        SELECT p.IdPcoCliente, p.Nome, p.Descricao, c.Nome AS Cliente, p.Ativo
        FROM PcoClientes p
        INNER JOIN Clientes c ON p.IdCliente = c.IdCliente
    """)
    pcos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_pco.html', clientes=clientes, pcos=pcos)


@cadastrar_pco_bp.route('/editar_pco/<int:id_pco>', methods=['GET'])
def editar_pco(id_pco):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os clientes
    cursor.execute("SELECT IdCliente, Nome FROM Clientes WHERE Ativo = 1")
    clientes = cursor.fetchall()

    # Consulta para obter os dados do PCO selecionado
    cursor.execute("""
        SELECT IdPcoCliente, Nome, Descricao, IdCliente, Ativo
        FROM PcoClientes
        WHERE IdPcoCliente = ?
    """, (id_pco,))
    pco = cursor.fetchone()

    cursor.close()
    conn.close()

    if not pco:
        flash('PCO não encontrado.', 'error')
        return redirect(url_for('cadastrar_pco.cadastrar_pco'))

    # Passa os dados para o template
    return render_template('editar_pco.html', clientes=clientes, pco=pco)


@cadastrar_pco_bp.route('/salvar_pco', methods=['POST'])
def salvar_pco():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    id_cliente = int(request.form['cliente'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        # Verifica se já existe um PCO com o mesmo nome (independente do cliente)
        cursor.execute("""
            SELECT IdPcoCliente FROM PcoClientes 
            WHERE Nome = ?
        """, (nome,))
        pco_existente = cursor.fetchone()
        
        if pco_existente:
            flash('Já existe um PCO cadastrado com este nome! O nome deve ser único.', 'error')
            return redirect(url_for('cadastrar_pco.cadastrar_pco'))

        # Insere o novo PCO na tabela PcoClientes
        query = """
        INSERT INTO PcoClientes (
            Nome, Descricao, IdCliente, Ativo
        ) VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (nome, descricao, id_cliente, ativo))
        conn.commit()
        flash('PCO cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o PCO: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_pco.cadastrar_pco'))


@cadastrar_pco_bp.route('/salvar_edicao_pco/<int:id_pco>', methods=['POST'])
def salvar_edicao_pco(id_pco):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    id_cliente = int(request.form['cliente'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        # Verifica se já existe outro PCO com o mesmo nome (excluindo o próprio)
        cursor.execute("""
            SELECT IdPcoCliente FROM PcoClientes 
            WHERE Nome = ? AND IdPcoCliente != ?
        """, (nome, id_pco))
        pco_existente = cursor.fetchone()
        
        if pco_existente:
            flash('Já existe outro PCO cadastrado com este nome! O nome deve ser único.', 'error')
            return redirect(url_for('cadastrar_pco.editar_pco', id_pco=id_pco))

        # Atualiza o PCO na tabela PcoClientes
        query = """
        UPDATE PcoClientes
        SET Nome = ?, Descricao = ?, IdCliente = ?, Ativo = ?
        WHERE IdPcoCliente = ?
        """
        cursor.execute(query, (nome, descricao, id_cliente, ativo, id_pco))
        conn.commit()
        flash('PCO atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o PCO: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_pco.cadastrar_pco'))