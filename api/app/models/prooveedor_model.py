from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, text, Integer
from . import db
from .base_model import BaseModelMixin


class Proveedor(BaseModelMixin, db.Model):
    __tablename__ = 'proveedores'
    
    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    nit = Column(String(16), nullable=False, unique=True)
    nombre = Column(String(255), nullable=False)
    informacion_contacto = Column(Text, nullable=True)   

    # Relaciones
    inventario = db.relationship('Inventario', back_populates='proveedor', cascade="all, delete-orphan")
    compras = db.relationship('Compras', back_populates='proveedor', cascade="all, delete-orphan")

    @staticmethod
    def get_proveedor_id(id_proveedor):
        """Obtiene un proveedor por su ID."""
        return Proveedor.query.filter_by(id_proveedor=id_proveedor, activo=True).first()

    @staticmethod
    def get_proveedor_nit(nit):
        """Obtiene un proveedor por su NIT."""
        return Proveedor.query.filter_by(nit=nit, activo=True).first()
    
    @staticmethod
    def get_proveedores():
        """Obtiene todos los proveedores activos."""
        return Proveedor.query.filter_by(activo=True).all()