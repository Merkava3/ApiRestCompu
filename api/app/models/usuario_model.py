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
    activo = Column(Boolean, default=True)

    # Relaciones
    servicios = db.relationship('Servicios', back_populates='usuario', cascade="all, delete-orphan")
    facturas = db.relationship('Facturas', back_populates='usuario', cascade="all, delete-orphan")
    compras = db.relationship('Compras', back_populates='usuario', cascade="all, delete-orphan")
    
    def generate_auth_token(self, expires_in=3600):
        """Genera un token JWT y actualiza los campos en la base de datos"""
        try:
            payload = {
                'sub': str(self.id_usuario),
                'email': str(self.email_usuario),
                'rol': self.rol,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
            token = jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY', 'fallback-secret-key'),
                algorithm='HS256'
            )
            
            if isinstance(token, bytes):
                token = token.decode('utf-8')
                
            self.token = token
            self.token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
            self.autenticado = True
            self.ultima_autenticacion = datetime.utcnow()
            
            return token
            
        except Exception as e:
            raise ValueError(f"No se pudo generar el token: {str(e)}")
    
    def revoke_token(self):
        """Invalida el token actual del usuario"""
        self.token = None
        self.token_expiration = None
        self.autenticado = False

    @staticmethod
    def check_token(token):
        """Verifica un token JWT y devuelve el usuario si es válido"""
        try:
            if not token:
                return None
                
            clean_token = token.strip()
            
            payload = jwt.decode(
                clean_token,
                os.getenv('JWT_SECRET_KEY', 'fallback-secret-key'),
                algorithms=['HS256']
            )
            usuario = Usuario.query.get(payload['sub'])
            
            if usuario and usuario.token == clean_token:
                return usuario
            return None
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_usuario(id_usuario):
        """Obtiene un usuario por su ID."""
        return Usuario.query.filter_by(id_usuario=id_usuario).first()
    
    @staticmethod
    def get_usuario_by_email(email_usuario):
        """Obtiene un usuario por su email."""
        return Usuario.query.filter_by(email_usuario=email_usuario).first()
    
    @staticmethod
    def get_usuarios():
        """Obtiene todos los usuarios activos."""
        return Usuario.query.filter_by(activo=True).all()