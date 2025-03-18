from flask import Blueprint, render_template, redirect, url_for, session

# Cria um Blueprint para as rotas de páginas
paginas_bp = Blueprint('paginas', __name__)

# Rota para Registrar Horas
@paginas_bp.route('/registrar_horas')
def registrar_horas():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('registrar_horas.html')

# Rota para Consultar Registros
@paginas_bp.route('/consultar_registros')
def consultar_registros():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('consultar_registros.html')

# Rota para Valor a Receber
@paginas_bp.route('/valor_a_receber')
def valor_a_receber():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('valor_a_receber.html')

# Rota para Cadastrar Usuário (apenas administradores)
@paginas_bp.route('/cadastrar_usuario')
def cadastrar_usuario():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))
    return render_template('cadastrar_usuario.html')

# Rota para Cadastrar Cliente (apenas administradores)
@paginas_bp.route('/cadastrar_cliente')
def cadastrar_cliente():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))
    return render_template('cadastrar_cliente.html')

# Rota para Cadastrar PCO (apenas administradores)
@paginas_bp.route('/cadastrar_pco')
def cadastrar_pco():
    if 'usuario_id' not in session or session['usuario_admin'] != 1:
        return redirect(url_for('auth.login'))
    return render_template('cadastrar_pco.html')