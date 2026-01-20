from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric, text, Integer
from . import db
from .base_model import BaseModelMixin


class Productos(BaseModelMixin, db.Model):
    __tablename__ = 'productos'
    
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre_producto = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_venta = Column(Numeric(10, 2), nullable=False, default=0)
    cantidad_stock = Column(db.Integer, nullable=False, default=0)
    

    # Relaciones
    inventario = db.relationship('Inventario', back_populates='producto', cascade="all, delete-orphan")
    detalle_factura = db.relationship('DetalleFactura', back_populates='producto', cascade="all, delete-orphan")
    detalle_compra = db.relationship('DetalleCompra', back_populates='producto', cascade="all, delete-orphan")
    
    @staticmethod
    def get_producto(id_producto):
        """Obtiene un producto por su ID."""
        return Productos.query.filter_by(id_producto=id_producto, activo=True).first()

    @staticmethod
    def get_productos():
        """Obtiene todos los productos activos."""
        return Productos.query.filter_by(activo=True).all()
    
    @staticmethod
    def get_productos_por_stock():
        """Obtiene todos los productos activos ordenados por cantidad de stock descendente."""
        return Productos.query.filter_by(activo=True).order_by(Productos.cantidad_stock.desc()).all()
