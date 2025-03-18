from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import db, Usuario

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        
        user = Usuario.query.filter_by(Usuario=usuario).first()
        
        if user and user.verificar_senha(senha):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))  # Substitua pela sua página inicial
        
        flash('Usuário ou senha incorretos', 'danger')

    return render_template('login.html')

@usuarios_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta', 'info')
    return redirect(url_for('usuarios.login'))
