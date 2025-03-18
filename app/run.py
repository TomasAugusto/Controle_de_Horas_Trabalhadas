from flask import Flask, render_template, redirect, url_for, session
from app.routes.auth import auth_bp  # Importação absoluta corrigida
from app.config import conectar_banco  # Importação absoluta corrigida

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar flash e session

# Registra o Blueprint de autenticação
app.register_blueprint(auth_bp, url_prefix='/')

# Rota principal redirecionando para login
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Página Home
@app.route('/home')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('home.html', usuario=session['usuario_nome'])

if __name__ == '__main__':
    app.run(debug=True)