from . import db
from .base_model import BaseModelMixin

class Productos(BaseModelMixin, db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre_producto = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    inventario = db.relationship('Inventario', back_populates='producto')
    detalle_factura = db.relationship('DetalleFactura', back_populates='producto')
    detalle_compra = db.relationship('DetalleCompra', back_populates='producto')
    
    @staticmethod
    def get_producto(id_producto):
        return Productos.query.filter_by(id_producto=id_producto).first()

    @staticmethod
    def get_productos():
        return Productos.query.all()
