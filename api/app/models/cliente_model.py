from sqlalchemy import Column, String, Text, Integer
from . import db
from .base_model import BaseModelMixin


class Cliente(BaseModelMixin, db.Model):
    __tablename__ = 'clientes'
    
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(16), nullable=False, unique=True)
    nombre_cliente = Column(String(255), nullable=False)
    direccion = Column(Text, nullable=True)
    telefono_cliente = Column(String(50), nullable=True)
    

    # Relaciones
    dispositivos = db.relationship('Dispositivo', back_populates='cliente', cascade="all, delete-orphan")
    servicios = db.relationship('Servicios', back_populates='cliente', cascade="all, delete-orphan")
    facturas = db.relationship('Facturas', back_populates='cliente', cascade="all, delete-orphan")

    @staticmethod
    def get_cliente(cedula):
        """Obtiene un cliente por su cédula."""
        return Cliente.query.filter_by(cedula=cedula, activo=True).first()
    
    @staticmethod
    def get_id_client(id_cliente):
        """Obtiene un cliente por su ID."""
        return Cliente.query.filter_by(id_cliente=id_cliente, activo=True).first()
    
    @staticmethod
    def get_clientes():
        """Obtiene todos los clientes activos."""
        return Cliente.query.filter_by(activo=True).all()
    
    @classmethod
    def count_clients(cls):
        """Cuenta el total de clientes activos."""
        return db.session.query(db.func.count(cls.cedula)).filter(cls.activo == True).scalar()
    
    @classmethod
    def get_last_three_clients(cls):
        """Obtiene los últimos 3 clientes activos ordenados por fecha de creación descendente."""
        return cls.query.filter_by(activo=True).order_by(cls.created_at.desc()).limit(3).all()