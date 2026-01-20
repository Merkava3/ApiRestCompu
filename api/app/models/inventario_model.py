from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, text
from . import db
from .base_model import BaseModelMixin


class Inventario(BaseModelMixin, db.Model):
    __tablename__ = 'inventario'
    
    id_inventario = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey('productos.id_producto'), nullable=False)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id_proveedor'), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, server_default=text("now()"))

    # Relaciones
    producto = db.relationship('Productos', back_populates='inventario')
    proveedor = db.relationship('Proveedor', back_populates='inventario')

    @staticmethod
    def get_inventario(id_inventario):
        """Obtiene un registro de inventario por su ID."""
        return Inventario.query.filter_by(id_inventario=id_inventario).first()
        
    @staticmethod
    def get_inventarios():
        """Obtiene todos los registros de inventario."""
        return Inventario.query.all()

    @staticmethod
    def get_inventario_by_producto(producto_id):
        """Obtiene todos los registros de inventario de un producto específico."""
        return Inventario.query.filter_by(producto_id=producto_id).order_by(Inventario.ultima_actualizacion.desc()).all()
    
    @staticmethod
    def get_inventario_by_proveedor(proveedor_id):
        """Obtiene todos los registros de inventario de un proveedor específico."""
        return Inventario.query.filter_by(proveedor_id=proveedor_id).order_by(Inventario.ultima_actualizacion.desc()).all()
