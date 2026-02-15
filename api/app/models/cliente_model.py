from sqlalchemy import Column, String, Text, Integer, Boolean
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

    @staticmethod
    def get_cliente(cedula):
        """Obtiene un cliente por su cédula."""
        return Cliente.query.filter_by(cedula=cedula).first()

    @staticmethod
    def get_id_client(id_cliente):
        """Obtiene un cliente por su ID."""
        return Cliente.query.filter_by(id_cliente=id_cliente).first()

    @staticmethod
    def get_clientes():
        """Obtiene todos los clientes."""
        return Cliente.query.all()

    @classmethod
    def count_clients(cls):
        """Cuenta el total de clientes."""
        return db.session.query(db.func.count(cls.cedula)).scalar()

    @classmethod
    def get_last_three_clients(cls):
        """Obtiene los últimos 3 clientes ordenados por ID descendente."""
        return cls.query.order_by(cls.id_cliente.desc()).limit(3).all()