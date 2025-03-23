from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta


cadastrar_atividade_bp = Blueprint('cadastrar_atividade', __name__)


#----------------------------------Cadastrar Atividade-------------------------------------------


@cadastrar_atividade_bp.route('/cadastrar_atividade', methods=['GET'])
def cadastrar_atividade():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter todas as atividades cadastradas
    cursor.execute("SELECT IdAtividade, Nome, Descricao, Ativo FROM Atividades")
    atividades = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_atividade.html', atividades=atividades)

@cadastrar_atividade_bp.route('/salvar_atividade', methods=['POST'])
def salvar_atividade():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere a nova atividade na tabela Atividades
    query = """
    INSERT INTO Atividades (
        Nome, Descricao, Ativo
    ) VALUES (?, ?, ?)
    """
    try:
        cursor.execute(query, (nome, descricao, ativo))
        conn.commit()
        flash('Atividade cadastrada com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao cadastrar a atividade: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_atividade.cadastrar_atividade'))

@cadastrar_atividade_bp.route('/editar_atividade/<int:id_atividade>', methods=['GET'])
def editar_atividade(id_atividade):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os dados da atividade selecionada
    cursor.execute("""
        SELECT IdAtividade, Nome, Descricao, Ativo
        FROM Atividades
        WHERE IdAtividade = ?
    """, (id_atividade,))
    atividade = cursor.fetchone()

    cursor.close()
    conn.close()

    if not atividade:
        flash('Atividade não encontrada.', 'error')
        return redirect(url_for('cadastrar_atividade.cadastrar_atividade'))

    # Passa os dados para o template
    return render_template('editar_atividade.html', atividade=atividade)


@cadastrar_atividade_bp.route('/salvar_edicao_atividade/<int:id_atividade>', methods=['POST'])
def salvar_edicao_atividade(id_atividade):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    nome = request.form['nome']
    descricao = request.form['descricao']
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza a atividade na tabela Atividades
    query = """
    UPDATE Atividades
    SET Nome = ?, Descricao = ?, Ativo = ?
    WHERE IdAtividade = ?
    """
    try:
        cursor.execute(query, (nome, descricao, ativo, id_atividade))
        conn.commit()
        flash('Atividade atualizada com sucesso!', 'success')
    except pyodbc.Error as e:
        conn.rollback()
        flash(f'Erro ao atualizar a atividade: {str(e)}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_atividade.cadastrar_atividade'))


