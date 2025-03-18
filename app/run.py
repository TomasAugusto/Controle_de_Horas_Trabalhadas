from flask import Flask, redirect, url_for
from app.routes.auth import auth_bp
from app.routes.paginas import paginas_bp

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar flash e session

# Registra os Blueprints
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(paginas_bp, url_prefix='/')

# Rota principal redirecionando para login
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)