from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint
from . import db
from .base_model import BaseModelMixin


class DetalleFactura(BaseModelMixin, db.Model):
    __tablename__ = 'detalle_factura'
    
    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    factura_id_detalle = Column(Integer, ForeignKey('facturas.id_factura', ondelete='CASCADE'), nullable=False)
    producto_id_detalle = Column(Integer, ForeignKey('productos.id_producto', ondelete='RESTRICT'), nullable=False)
    cantidad_detalle = Column(Integer, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Constraint único
    __table_args__ = (UniqueConstraint('factura_id_detalle', 'producto_id_detalle', name='uq_factura_producto'),)
    
    # Relaciones
    factura = db.relationship('Facturas', back_populates='detalle_factura')
    producto = db.relationship('Productos', back_populates='detalle_factura')

    @staticmethod
    def get_detalle_factura(id_detalle):
        """Obtiene un detalle de factura por su ID."""
        return DetalleFactura.query.filter_by(id_detalle=id_detalle).first()
    
    @staticmethod
    def get_detalle_facturas():
        """Obtiene todos los detalles de factura."""
        return DetalleFactura.query.all()
    
    @staticmethod
    def get_detalle_facturas_by_factura(factura_id):
        """Obtiene todos los detalles de una factura específica."""
        return DetalleFactura.query.filter_by(factura_id_detalle=factura_id).all()
