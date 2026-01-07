"""
Modelo Cliente - Refactorizado usando BaseModelMixin.
Elimina código duplicado en métodos save/delete usando herencia múltiple.
"""
from sqlalchemy import Column, Integer, String, Text
from . import db
from .base_model import BaseModelMixin


class Cliente(BaseModelMixin, db.Model):
    """Modelo de Cliente con funcionalidad base proporcionada por BaseModelMixin."""
    __tablename__ = 'clientes'
    
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(16), nullable=False, unique=True)
    nombre_cliente = Column(String(255), nullable=False)
    direccion = Column(Text, nullable=False)
    telefono_cliente = Column(String(50), nullable=False)

    # Relaciones
    dispositivos = db.relationship('Dispositivo', back_populates='cliente', cascade="all, delete-orphan")
    servicios = db.relationship('Servicios', back_populates='cliente', cascade="all, delete-orphan")
    facturas = db.relationship('Facturas', back_populates='cliente', cascade="all, delete-orphan")

    # Métodos de consulta
    @staticmethod
    def get_cliente(cedula):
        """Obtiene un cliente por su cédula."""
        return Cliente.query.filter_by(cedula=cedula).first()
    
    @staticmethod
    def get_id_client(id_cliente):
        """Obtiene un cliente por su ID."""
        return Cliente.query.filter_by(id_cliente=id_cliente).first()
    
    @classmethod
    def count_clients(cls):
        """Cuenta el total de clientes."""
        return db.session.query(db.func.count(cls.cedula)).scalar()
    
    @classmethod
    def get_last_three_clients(cls):
        """Obtiene los últimos 3 clientes ordenados por cédula descendente."""
        return cls.query.order_by(cls.cedula.desc()).limit(3).all()
    
    # Los métodos save(), delete(), new(), create_from_dict() y update_from_dict()
    # son heredados de BaseModelMixin, eliminando código duplicado