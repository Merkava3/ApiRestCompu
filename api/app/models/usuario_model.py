from . import db
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean
import secrets

bcrypt = Bcrypt()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(255), nullable=False)
    email_usuario = Column(Text, nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    autenticado = Column(Boolean, default=False)
    ultima_autenticacion = Column(TIMESTAMP, default=datetime.utcnow, nullable=True)
    token = Column(String(255), unique=True, nullable=True)
    token_expiration = Column(TIMESTAMP, nullable=True)

    servicios = db.relationship('Servicios', back_populates='usuario', cascade="all, delete-orphan")
    facturas = db.relationship('Facturas', back_populates='usuario', cascade="all, delete-orphan")
    compras = db.relationship('Compras', back_populates='usuario', cascade="all, delete-orphan")

    def generate_auth_token(self, expires_in=3600):
        self.token = secrets.token_urlsafe(32)
        self.token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        self.autenticado = True
        self.ultima_autenticacion = datetime.utcnow()
        return self.token
    
    def revoke_token(self):
        self.token = None
        self.token_expiration = None
        self.autenticado = False

    @staticmethod
    def check_token(token):
        usuario = Usuario.query.filter_by(token=token).first()
        if usuario is None or usuario.token_expiration < datetime.utcnow():
            return None
        return usuario
     
    def set_password(self, password):
        """Encripta la contraseña antes de almacenarla"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con la almacenada"""
        return check_password_hash(self.password, password)

    @staticmethod
    def get_user(email_usuario):
        return Usuario.query.filter_by( email_usuario= email_usuario).first()
    
    @staticmethod
    def get_user_id(id_usuario):
        return Usuario.query.filter_by(id_usuario=id_usuario).first()

    @classmethod
    def new(cls, **kwargs):
        return cls(**kwargs)  # Usar cls en lugar de Usuario para flexibilidad

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError: {e}")
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Exception: {e.__class__.__name__}: {e}")
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Exception: {e.__class__.__name__}: {e}")
            return False

    def __str__(self):
        return f"Usuario: {self.nombre_usuario} - {self.email_usuario}"  