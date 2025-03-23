from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta

cadastrar_servico_bp = Blueprint('cadastrar_servico', __name__)


#----------------------------------Cadastrar Serviço-------------------------------------------


@cadastrar_servico_bp.route('/cadastrar_servico', methods=['GET'])
def cadastrar_servico():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todos os serviços cadastrados
    cursor.execute("SELECT IdServico, Nome, Descricao, Ativo FROM Servicos")
    servicos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_servico.html', servicos=servicos)


@cadastrar_servico_bp.route('/salvar_servico', methods=['POST'])
def salvar_servico():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo serviço na tabela Servicos
    query = """
    INSERT INTO Servicos (
        Nome, Descricao, Ativo
    ) VALUES (?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, ativo))
        conn.commit()
        flash('Serviço cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o serviço: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_servico.cadastrar_servico'))


@cadastrar_servico_bp.route('/editar_servico/<int:id_servico>', methods=['GET'])
def editar_servico(id_servico):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados do serviço selecionado
    cursor.execute("""
        SELECT IdServico, Nome, Descricao, Ativo
        FROM Servicos
        WHERE IdServico = ?
    """, (id_servico,))
    servico = cursor.fetchone()

    cursor.close()
    conn.close()

    if not servico:
        flash('Serviço não encontrado.', 'error')
        return redirect(url_for('cadastrar_servico.cadastrar_servico'))

    # Passa os dados para o template
    return render_template('editar_servico.html', servico=servico)


@cadastrar_servico_bp.route('/salvar_edicao_servico/<int:id_servico>', methods=['POST'])
def salvar_edicao_servico(id_servico):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o serviço na tabela Servicos
    query = """
    UPDATE Servicos
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdServico = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_servico))
        conn.commit()
        flash('Serviço atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o serviço: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_servico.cadastrar_servico'))

