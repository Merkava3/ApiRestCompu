from datetime import datetime, timedelta
import os
import jwt
from sqlalchemy import Column, String, Boolean, DateTime, Enum, text, Integer
from . import db
from .base_model import BaseModelMixin
from ..helpers.const import ROLES_USUARIO

bcrypt_available = False
try:
    from flask_bcrypt import Bcrypt
    bcrypt_available = True
    bcrypt = Bcrypt()
except ImportError:
    pass

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'D5*F?_1?-d$f*1')
JWT_ALGORITHM = "HS256"


class Usuario(BaseModelMixin, db.Model):
    __tablename__ = 'usuarios'
        
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(255), nullable=False)
    email_usuario = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    rol = Column(Enum(*ROLES_USUARIO, name='rol_enum'), nullable=False, default='vendedor')
    autenticado = Column(Boolean, default=False)
    ultima_autenticacion = Column(DateTime, nullable=True)
    token = Column(String(255), nullable=True)
    token_expiration = Column(DateTime, nullable=True)    

    # Relaciones con otros modelos
    servicios = db.relationship('Servicios', back_populates='usuario', cascade="all, delete-orphan")
    
    def generate_auth_token(self, expires_in=3600):
        # Genera un token JWT y actualiza el estado del usuario
        try:
            now = datetime.utcnow()
            payload = {
                'sub': str(self.id_usuario),
                'email': str(self.email_usuario),
                'rol': self.rol,
                'iat': now,
                'exp': now + timedelta(seconds=expires_in)
            }
            
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            if isinstance(token, bytes): token = token.decode('utf-8')
                
            self.token = token
            self.token_expiration = now + timedelta(seconds=expires_in)
            self.autenticado = True
            self.ultima_autenticacion = now
            return token
        except Exception as e:
            raise ValueError(f"Error generando token: {str(e)}")
    
    def revoke_token(self):
        # Invalida la sesion actual del usuario
        self.token = None
        self.token_expiration = None
        self.autenticado = False

    def set_password(self, password):
        # Hashea la contraseña antes de guardar
        if bcrypt_available:
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        else:
            self.password = password

    @staticmethod
    def verify_password(password_hash, password):
        # Verifica el hash de la contraseña de forma estática
        if bcrypt_available:
            try:
                return bcrypt.check_password_hash(password_hash, password)
            except Exception:
                return False
        return password_hash == password

    @staticmethod
    def check_token(token):
        # Valida un token JWT y retorna el usuario correspondiente
        try:
            if not token: return None
            payload = jwt.decode(token.strip(), JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user = Usuario.query.get(payload['sub'])
            return user if user and user.token == token.strip() else None
        except:
            return None

    # --- Consultas directas ---
    @staticmethod
    def get_by_email(email): 
        return Usuario.query.filter_by(email_usuario=email).first()

    @staticmethod
    def get_by_id(user_id): 
        return Usuario.query.get(user_id)

    @staticmethod
    def get_active_users(): 
        return Usuario.query.all()

    # --- Procedimientos Almacenados ---
    @staticmethod
    def call_login_sp(email):
        # Llama a fn_login_usuario para login y expiracion
        try:
            return db.session.execute(text("SELECT fn_login_usuario(:email)"), {"email": email}).scalar()
        except Exception as e:
            print(f"Error login SP: {e}")
            return None

    @staticmethod
    def call_logout_sp(email):
        # Llama a fn_logout_usuario para cierre de sesion
        try:
            return db.session.execute(text("SELECT fn_logout_usuario(:email)"), {"email": email}).scalar()
        except Exception as e:
            print(f"Error logout SP: {e}")
            return None