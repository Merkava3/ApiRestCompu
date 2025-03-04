from . import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(255), nullable=False)
    email_usuario = Column(Text, nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    autenticado = Column(Boolean, default=False)
    ultima_autenticacion = Column(TIMESTAMP, nullable=True)

    @staticmethod
    def get_user(email_usuario):
        return Usuario.query.filter_by( email_usuario= email_usuario).first()

    @classmethod
    def new(cls, **kwargs):
        return Usuario(**kwargs)

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
        return f"Usuario: {self.nombre_usuario} {self.apellido_usuario} - {self.email_usuario}"

