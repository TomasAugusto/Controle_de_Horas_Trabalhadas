# routes/paginas.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request ,jsonify
from app.config import conectar_banco
import pyodbc
from datetime import datetime, timedelta


# Cria um Blueprint para as rotas de páginas
paginas_bp = Blueprint('paginas', __name__)

# Rota para a página Home
@paginas_bp.route('/home')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('home.html', usuario=session['usuario_nome'])
