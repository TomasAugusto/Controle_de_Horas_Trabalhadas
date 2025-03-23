from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta

cadastrar_usuario_bp = Blueprint('cadastrar_usuario', __name__)


#----------------------------------Cadastrar Usuário-------------------------------------------

# Rota para Cadastrar Usuário (apenas administradores)
@cadastrar_usuario_bp.route('/cadastrar_usuario', methods=['GET'])
def cadastrar_usuario():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os setores
    cursor.execute("SELECT IdSetor, Nome FROM Setores WHERE Ativo = 1")
    setores = cursor.fetchall()

    # Consulta para obter todos os usuários cadastrados
    cursor.execute("""
        SELECT u.IdUsuario, u.Usuario, u.ValorHora, s.Nome AS Setor, u.Administrador, u.Ativo
        FROM Usuarios u
        INNER JOIN Setores s ON u.Setor = s.IdSetor
    """)
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    # Passa os dados para o template
    return render_template('cadastrar_usuario.html', setores=setores, usuarios=usuarios)

@cadastrar_usuario_bp.route('/salvar_usuario', methods=['POST'])
def salvar_usuario():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    usuario = request.form['usuario']
    senha = request.form['senha']
    valor_hora = float(request.form['valor_hora'])
    setor = int(request.form['setor'])
    administrador = int(request.form['administrador'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Insere o novo usuário na tabela Usuarios
    query = """
    INSERT INTO Usuarios (
        Usuario, Senha, ValorHora, Setor, Administrador, DataCadastro, Ativo
    ) VALUES (?, ?, ?, ?, ?, GETDATE(), ?)
    """
    try:
        cursor.execute(query, (usuario, senha, valor_hora, setor, administrador, ativo))
        conn.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
    except pyodbc.IntegrityError as e:
        conn.rollback()
        flash('Erro ao cadastrar o usuário. Verifique os dados e tente novamente.', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cadastrar_usuario.cadastrar_usuario'))


@cadastrar_usuario_bp.route('/editar_usuario/<int:id_usuario>', methods=['GET'])
def editar_usuario(id_usuario):
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Consulta para obter os setores
    cursor.execute("SELECT IdSetor, Nome FROM Setores WHERE Ativo = 1")
    setores = cursor.fetchall()

    # Consulta para obter os dados do usuário selecionado
    cursor.execute("""
        SELECT IdUsuario, Usuario, ValorHora, Setor, Administrador, Ativo
        FROM Usuarios
        WHERE IdUsuario = ?
    """, (id_usuario,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if not usuario:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('cadastrar_usuario.cadastrar_usuario'))

    # Passa os dados para o template
    return render_template('editar_usuario.html', setores=setores, usuario=usuario)

@cadastrar_usuario_bp.route('/salvar_edicao_usuario/<int:id_usuario>', methods=['POST'])
def salvar_edicao_usuario(id_usuario):
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))

    # Obtém os dados do formulário
    usuario = request.form['usuario']
    senha = request.form['senha']
    valor_hora = float(request.form['valor_hora'])
    setor = int(request.form['setor'])
    administrador = int(request.form['administrador'])
    ativo = int(request.form['ativo'])

    # Conecta ao banco de dados
    conn = conectar_banco()
    cursor = conn.cursor()

    # Atualiza o usuário na tabela Usuarios
    if senha:
        query = """
        UPDATE Usuarios
        SET Usuario = ?, Senha = ?, ValorHora = ?, Setor = ?, Administrador = ?, Ativo = ?
        WHERE IdUsuario = ?
        """
        cursor.execute(query, (usuario, senha, valor_hora, setor, administrador, ativo, id_usuario))
    else:
        query = """
        UPDATE Usuarios
        SET Usuario = ?, ValorHora = ?, Setor = ?, Administrador = ?, Ativo = ?
        WHERE IdUsuario = ?
        """
        cursor.execute(query, (usuario, valor_hora, setor, administrador, ativo, id_usuario))

    conn.commit()
    cursor.close()
    conn.close()

    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('cadastrar_usuario.cadastrar_usuario'))

