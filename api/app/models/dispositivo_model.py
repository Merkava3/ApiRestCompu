from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from . import db

class Dispositivo(db.Model):
    __tablename__ = 'dispositivos'  # Nombre de la tabla

    # Columnas de la tabla
    id_dispositivo = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    cliente_id_dispositivo = db.Column(db.BigInteger, db.ForeignKey('clientes.id_cliente'), nullable=False)
    tipo = db.Column(db.String(255), nullable=False)
    marca = db.Column(db.String(255), nullable=False)
    modelo = db.Column(db.String(255), nullable=False)
    reporte = db.Column(db.Text, nullable=False)
    numero_serie = db.Column(db.String(255), nullable=False, unique=True)
    fecha_ingreso = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relación con la tabla de clientes (si existe)
    cliente = db.relationship('Cliente', back_populates='dispositivos')

    # Métodos de la clase
    @staticmethod
    def get_dispositivo(numero_serie):  # Método estático para obtener un dispositivo por su número de serie
        return Dispositivo.query.filter_by(numero_serie=numero_serie).first()

    @classmethod
    def new(cls, kwargs):  # Convierte un diccionario en un objeto Dispositivo
        return Dispositivo(**kwargs)

    @staticmethod
    def get_all():
        """Obtiene todos los dispositivos almacenados en la base de datos."""
        return Dispositivo.query.all()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()  # Deshace la transacción en caso de error
            print(f"Error en save: {e}")  # Imprime el error para depuración
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()  # Deshace la transacción en caso de error
            print(f"Error en delete: {e}")  # Imprime el error para depuración
            return False

    def __str__(self):
        return self.numero_serie  # Representación en string del objeto