from flask import Flask, redirect, url_for
from app.routes.auth import auth_bp
from app.routes.paginas import paginas_bp
from app.routes.cadastrar_atividade import cadastrar_atividade_bp
from app.routes.cadastrar_cliente import cadastrar_cliente_bp
from app.routes.cadastrar_pco import cadastrar_pco_bp
from app.routes.cadastrar_servico import cadastrar_servico_bp
from app.routes.cadastrar_setor import cadastrar_setor_bp
from app.routes.cadastrar_usuario import cadastrar_usuario_bp
from app.routes.consultar_registros import consultar_registros_bp
from app.routes.registrar_horas import registrar_horas_bp
from app.routes.valor_a_receber import valor_a_receber_bp



app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar flash e session

# Registra os Blueprints
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(paginas_bp, url_prefix='/')
app.register_blueprint(cadastrar_atividade_bp, url_prefix='/')
app.register_blueprint(cadastrar_cliente_bp, url_prefix='/')
app.register_blueprint(cadastrar_pco_bp, url_prefix='/')
app.register_blueprint(cadastrar_servico_bp, url_prefix='/')
app.register_blueprint(cadastrar_setor_bp, url_prefix='/')
app.register_blueprint(cadastrar_usuario_bp, url_prefix='/')
app.register_blueprint(consultar_registros_bp, url_prefix='/')
app.register_blueprint(registrar_horas_bp, url_prefix='/')
app.register_blueprint(valor_a_receber_bp, url_prefix='/')


# Rota principal redirecionando para login
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)

    