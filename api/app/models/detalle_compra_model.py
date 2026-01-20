from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint
from . import db
from .base_model import BaseModelMixin


class DetalleCompra(BaseModelMixin, db.Model):
    __tablename__ = 'detalles_compras'
    
    id_detalles_compras = Column(Integer, primary_key=True, autoincrement=True)
    compras_id_detalles = Column(Integer, ForeignKey('compras.id_compras', ondelete='CASCADE'), nullable=False)
    producto_id_detalles = Column(Integer, ForeignKey('productos.id_producto', ondelete='RESTRICT'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    
    # Constraint único
    __table_args__ = (UniqueConstraint('compras_id_detalles', 'producto_id_detalles', name='uq_compra_producto'),)

    # Relaciones
    compras = db.relationship('Compras', back_populates='detalle_compra')
    producto = db.relationship('Productos', back_populates='detalle_compra')

    @staticmethod
    def get_detalle_compra(id_detalle_compra):
        """Obtiene un detalle de compra por su ID."""
        return DetalleCompra.query.filter_by(id_detalles_compras=id_detalle_compra).first()
    
    @staticmethod
    def get_detalle_compras():
        """Obtiene todos los detalles de compra."""
        return DetalleCompra.query.all()
    
    @staticmethod
    def get_detalle_compras_by_compra(compra_id):
        """Obtiene todos los detalles de una compra específica."""
        return DetalleCompra.query.filter_by(compras_id_detalles=compra_id).all()