from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..config import conectar_banco  # Importação relativa corrigida

# Cria um Blueprint para as rotas de autenticação
auth_bp = Blueprint('auth', __name__)

# Rota de login
@auth_bp.route('/usuarios/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Consulta para verificar se o usuário existe e a senha está correta
        cursor.execute("SELECT IdUsuario, Usuario FROM Usuarios WHERE Usuario = ? AND Senha = ?", (usuario, senha))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['usuario_id'] = user[0]  # Guarda o ID na sessão
            session['usuario_nome'] = user[1]  # Guarda o nome na sessão
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos', 'error')

    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))