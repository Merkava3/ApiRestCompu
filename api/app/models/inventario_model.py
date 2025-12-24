from . import db
from datetime import datetime
from  .producto_model import Productos
from .prooveedor_model  import Proveedor
from  ..helpers.const import INSERTAR_INVENTARIO, COLUMN_LIST_INVENTARIO
from ..helpers.helpers import Help
from sqlalchemy import text

class Inventario(db.Model):
    __tablename__ = 'inventario'
    id_inventario = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_producto_inventario = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto'), nullable=False)
    id_proveedor_inventario = db.Column(db.BigInteger, db.ForeignKey('proveedores.id_proveedor'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    ultima_actualizacion = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)

    producto = db.relationship('Productos', back_populates='inventario')
    proveedor = db.relationship('Proveedor', back_populates='inventario')

    @staticmethod
    def get_inventario(id_inventario):
        return Inventario.query.filter_by(id_inventario=id_inventario).first()
        
    @staticmethod
    def get_inventarios():
        return Inventario.query.all()
    
    @classmethod
    def new(cls, kwargs):
        return Inventario(**kwargs)
    
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except:
            return False
    
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar inventario: {e}")  # Para depuración

    @staticmethod
    def get_inventario_query():
        return db.session.query(
            Inventario.id_inventario,
            Productos.id_producto,
            Proveedor.nit,
            Proveedor.nombre_proveedor,
            Productos.nombre_producto,
            Productos.precio,
            Productos.stock,
            Inventario.cantidad,            
            func.to_char(Inventario.ultima_actualizacion, 'DD/MM/YYYY').label('ultima_actualizacion'),
        ).join(Productos, Inventario.id_producto_inventario == Productos.id_producto) \
         .join(Proveedor, Inventario.id_proveedor_inventario == Proveedor.id_proveedor) \
         .order_by(Productos.stock.desc()).all()
    
    @staticmethod
    def get_inventario_by_producto(id_producto):
        return db.session.query(
            Inventario.id_inventario,
            Productos.id_producto,
            Proveedor.nit,
            Proveedor.nombre_proveedor,
            Productos.nombre_producto,
            Productos.precio,
            Productos.stock,
            Inventario.cantidad,
            Inventario.ultima_actualizacion
        ).join(Productos, Inventario.id_producto_inventario == Productos.id_producto) \
        .join(Proveedor, Inventario.id_proveedor_inventario == Proveedor.id_proveedor) \
        .filter(Productos.id_producto == id_producto) \
        .order_by(Inventario.ultima_actualizacion.desc()) \
        .all()
    
    @classmethod
    def insertar_inventario_producto(cls, data):
        """Llama al procedimiento almacenado usando extract_params para limpiar el código."""
        try:           
            query_params = Help.extract_params_inventario(data, COLUMN_LIST_INVENTARIO)            
            query = text(INSERTAR_INVENTARIO)
            db.session.execute(query, query_params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al insertar inventario: {e}")  # Para depuración

    
 