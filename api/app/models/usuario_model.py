from . import db
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean
from dotenv import load_dotenv
import jwt
import os

load_dotenv()

bcrypt = Bcrypt()
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'D5*F?_1?-d$f*1')
JWT_ALGORITHM = "HS256" # Algoritmo de encriptación

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
        """Genera un token JWT y actualiza los campos en la base de datos"""
        try:
            # 1. Crear payload del token
            payload = {
                'sub': str(self.id_usuario),  # Asegurar que es string
                'email': str(self.email_usuario),
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
            # 2. Generar el token JWT
            token = jwt.encode(
                payload,
                os.getenv('JWT_SECRET_KEY', 'fallback-secret-key'),  # Clave segura
                algorithm='HS256'
            )
            
            # 3. Asegurar que el token es un string (PyJWT puede devolver bytes)
            if isinstance(token, bytes):
                token = token.decode('utf-8')
                
            # 4. Actualizar los campos en el modelo
            self.token = token
            self.token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
            self.autenticado = True
            
            # 5. Retornar el token generado
            return token
            
        except Exception as e:
            # Log detallado del error
            print(f"Error generando token para usuario {self.id_usuario}: {str(e)}")
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
                
            # Limpieza básica del token (por si hay espacios o caracteres raros)
            clean_token = token.strip()
            
            payload = jwt.decode(
                clean_token,
                os.getenv('JWT_SECRET_KEY', 'fallback-secret-key'),
                algorithms=['HS256']
            )
            usuario = Usuario.query.get(payload['sub'])
            
            # Verificación adicional de coincidencia de token
            if usuario and usuario.token == clean_token:
                return usuario
            return None
            
        except jwt.ExpiredSignatureError:
            print("Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Token inválido: {str(e)}")
            return None
        except Exception as e:
            print(f"Error verificando token: {str(e)}")
            return None
     
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