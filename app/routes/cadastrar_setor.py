from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta

cadastrar_setor_bp = Blueprint('cadastrar_setor', __name__)


#----------------------------------Cadastrar Setor-------------------------------------------


@cadastrar_setor_bp.route('/cadastrar_setor', methods=['GET'])
def cadastrar_setor():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todos os setores cadastrados
    cursor.execute("SELECT IdSetor, Nome, Descricao, Ativo FROM Setores")
    setores = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_setor.html', setores=setores)


@cadastrar_setor_bp.route('/salvar_setor', methods=['POST'])
def salvar_setor():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo setor na tabela Setores
    query = """
    INSERT INTO Setores (
        Nome, Descricao, Ativo
    ) VALUES (?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, ativo))
        conn.commit()
        flash('Setor cadastrado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar o setor: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_setor.cadastrar_setor'))


@cadastrar_setor_bp.route('/editar_setor/<int:id_setor>', methods=['GET'])
def editar_setor(id_setor):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados do setor selecionado
    cursor.execute("""
        SELECT IdSetor, Nome, Descricao, Ativo
        FROM Setores
        WHERE IdSetor = ?
    """, (id_setor,))
    setor = cursor.fetchone()

    cursor.close()
    conn.close()

    if not setor:
        flash('Setor não encontrado.', 'error')
        return redirect(url_for('cadastrar_setor.cadastrar_setor'))

    # Passa os dados para o template
    return render_template('editar_setor.html', setor=setor)

@cadastrar_setor_bp.route('/salvar_edicao_setor/<int:id_setor>', methods=['POST'])
def salvar_edicao_setor(id_setor):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o setor na tabela Setores
    query = """
    UPDATE Setores
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdSetor = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_setor))
        conn.commit()
        flash('Setor atualizado com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar o setor: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_setor.cadastrar_setor'))

