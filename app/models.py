from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

class Usuario(db.Model, UserMixin):
    __tablename__ = "Usuarios"

    IdUsuario = db.Column(db.Integer, primary_key=True)
    Usuario = db.Column(db.String(100), unique=True, nullable=False)
    Senha = db.Column(db.String(255), nullable=False)
    Administrador = db.Column(db.Boolean, default=False)

    def set_senha(self, senha):
        self.Senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    def verificar_senha(self, senha):
        return bcrypt.check_password_hash(self.Senha, senha)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
