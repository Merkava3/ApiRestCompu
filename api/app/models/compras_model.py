from datetime import datetime
from sqlalchemy import Column, DateTime, Numeric, ForeignKey, Enum, text, Integer
from . import db
from .base_model import BaseModelMixin
from ..helpers.const import METODOS_PAGO


class Compras(BaseModelMixin, db.Model):
    __tablename__ = 'compras'
    
    id_compras = Column(Integer, primary_key=True, autoincrement=True)
    proveedor_id_compras = Column(Integer, ForeignKey('proveedores.id_proveedor'), nullable=False)   
    usuario_id_compras = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)    
    fecha_compras = Column(DateTime, default=datetime.utcnow, server_default=text("now()"))
    total_compras = Column(Numeric(10, 2), nullable=False, default=0)
    metodo_pago = Column(Enum(*METODOS_PAGO, name='metodo_pago_enum'), nullable=False)
   

    # Relaciones
    usuario = db.relationship('Usuario', back_populates='compras')
    proveedor = db.relationship('Proveedor', back_populates='compras')
    detalle_compra = db.relationship('DetalleCompra', back_populates='compras', cascade="all, delete-orphan")

    @staticmethod
    def get_compra(id_compra):
        """Obtiene una compra por su ID."""
        return Compras.query.filter_by(id_compras=id_compra, activo=True).first()
    
    @staticmethod
    def get_compras():
        """Obtiene todas las compras activas."""
        return Compras.query.filter_by(activo=True).order_by(Compras.fecha_compras.desc()).all()
    
    @staticmethod
    def get_compras_by_usuario(usuario_id):
        """Obtiene todas las compras de un usuario específico."""
        return Compras.query.filter_by(usuario_id_compras=usuario_id, activo=True).order_by(Compras.fecha_compras.desc()).all()
    
    @staticmethod
    def get_compras_by_proveedor(proveedor_id):
        """Obtiene todas las compras de un proveedor específico."""
        return Compras.query.filter_by(proveedor_id_compras=proveedor_id, activo=True).order_by(Compras.fecha_compras.desc()).all()
    
    
    
