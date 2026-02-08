from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, text, Integer
from . import db
from .base_model import BaseModelMixin


class Dispositivo(BaseModelMixin, db.Model):
    __tablename__ = 'dispositivos'

    id_dispositivo = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id_dispositivo = Column(Integer, ForeignKey('clientes.id_cliente', ondelete='CASCADE'), nullable=False)
    tipo = Column(String(255), nullable=False)
    marca = Column(String(255), nullable=False)
    modelo = Column(String(255), nullable=False)
    numero_serie = Column(String(255), nullable=False)
    reporte = Column(Text, nullable=True)
    fecha_ingreso = Column(DateTime, default=datetime.utcnow, server_default=text("now()"))


    # Relación con Cliente
    cliente = db.relationship('Cliente', back_populates='dispositivos')
    # Relaciones con Servicios
    servicios = db.relationship('Servicios', back_populates='dispositivo', cascade="all, delete-orphan")

    @staticmethod
    def get_dispositivo(numero_serie):
        """Obtiene un dispositivo por su número de serie."""
        return Dispositivo.query.filter_by(numero_serie=numero_serie, activo=True).first()

    @staticmethod
    def get_id_dispositivo(id_dispositivo):
        """Obtiene un dispositivo por su ID."""
        return Dispositivo.query.filter_by(id_dispositivo=id_dispositivo, activo=True).first()

    @staticmethod
    def get_dispositivos():
        """Obtiene todos los dispositivos activos."""
        return Dispositivo.query.filter_by(activo=True).all()

    @staticmethod
    def get_dispositivos_by_cliente(cliente_id):
        """Obtiene todos los dispositivos de un cliente específico."""
        return Dispositivo.query.filter_by(cliente_id_dispositivo=cliente_id, activo=True).all()

    def __str__(self):
        return self.numero_serie  # Representación en string del objeto
