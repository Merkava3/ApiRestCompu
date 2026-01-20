from datetime import datetime
from sqlalchemy import Column, DateTime, Boolean, Numeric, ForeignKey, text, Integer
from . import db
from .base_model import BaseModelMixin


class Facturas(BaseModelMixin, db.Model):
    __tablename__ = 'facturas'
    
    id_factura = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id_factura = Column(Integer, ForeignKey('clientes.id_cliente'), nullable=False)
    usuario_id_factura = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, server_default=text("now()"))
    pago = Column(Numeric(10, 2), nullable=False, default=0)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', back_populates='facturas')
    cliente = db.relationship('Cliente', back_populates='facturas')
    detalle_factura = db.relationship('DetalleFactura', back_populates='factura', cascade="all, delete-orphan")

    @staticmethod
    def get_factura(id_factura):
        """Obtiene una factura por su ID."""
        return Facturas.query.filter_by(id_factura=id_factura, activo=True).first()
    
    @staticmethod
    def get_facturas():
        """Obtiene todas las facturas activas."""
        return Facturas.query.filter_by(activo=True).order_by(Facturas.fecha.desc()).all()
    
    @staticmethod
    def get_facturas_by_cliente(cliente_id):
        """Obtiene todas las facturas de un cliente específico."""
        return Facturas.query.filter_by(cliente_id_factura=cliente_id, activo=True).order_by(Facturas.fecha.desc()).all()
    
    @staticmethod
    def get_facturas_by_usuario(usuario_id):
        """Obtiene todas las facturas de un usuario específico."""
        return Facturas.query.filter_by(usuario_id_factura=usuario_id, activo=True).order_by(Facturas.fecha.desc()).all()
   