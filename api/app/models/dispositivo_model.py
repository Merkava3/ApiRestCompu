from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from .cliente_model import Cliente
from sqlalchemy import text
from ..helpers.helpers import Help
from ..helpers.const import INSERTAR_CLIENTE_DISPOSITIVO, COLUMN_LIST_CLIENTE_DISPOSITIVO
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
    numero_serie = db.Column(db.String(255), nullable=False)
    fecha_ingreso = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relación con la tabla de clientes (si existe)
    cliente = db.relationship('Cliente', back_populates='dispositivos')
    reparaciones = db.relationship('Reparaciones', back_populates='dispositivo', cascade="all, delete-orphan")
    servicios = db.relationship('Servicios', back_populates='dispositivos', cascade="all, delete-orphan")

    # Métodos de la clase
    @staticmethod
    def get_dispositivo(numero_serie):  # Método estático para obtener un dispositivo por su número de serie
        return Dispositivo.query.filter_by(numero_serie=numero_serie).first()
    
    @staticmethod
    def get_id_dispositivo(id_dispositivo):
        return Dispositivo.query.filter_by(id_dispositivo =id_dispositivo).first()

    @classmethod
    def new(cls, kwargs):  # Convierte un diccionario en un objeto Dispositivo
        return Dispositivo(**kwargs)
        
    def get_dispositivos_con_clientes():
        """
        Retorna dispositivos con clientes usando una tupla de campos.
        """
        return db.session.query(
            Dispositivo.fecha_ingreso,
            Dispositivo.tipo,
            Dispositivo.modelo,
            Dispositivo.marca,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente
        ).join(Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente).all()
    
    @staticmethod
    def get_dispositivo_filter(cedula=None, numero_serie=None):
        """
        Obtiene dispositivos filtrando por cédula o número de serie.
        Si ambos valores son None, devuelve todos los dispositivos con clientes.
        """
        query = db.session.query(
            Dispositivo.fecha_ingreso,
            Dispositivo.tipo,
            Dispositivo.modelo,
            Dispositivo.marca,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente 
        ).join(Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente)
        if cedula:
            query = query.filter(Cliente.cedula == cedula)            
        if numero_serie:
            query = query.filter(Dispositivo.numero_serie == numero_serie)       
        return query.first()
        

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
    
    @classmethod
    def insertar_dispositivo(cls, data):
        """Llama al procedimiento almacenado usando extract_params para limpiar el código."""
        try:           
            query_params = Help.extract_params_cliente_dispositivo(data, COLUMN_LIST_CLIENTE_DISPOSITIVO)            
            query = text(INSERTAR_CLIENTE_DISPOSITIVO)
            db.session.execute(query, query_params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al insertar dispositivo: {e}")