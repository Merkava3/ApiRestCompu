from . import db
from sqlalchemy import text
from datetime import datetime
from ..helpers.helpers import Help
from ..helpers.const import INSERTAR_COMPRA, COLUMN_LIST_COMPRA

class Compras(db.Model):
    __tablename__ = 'compras'
    id_compras = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    total_compras = db.Column(db.Float, nullable=False)
    fecha_compras = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    id_proveedor_compras = db.Column(db.BigInteger, db.ForeignKey('proveedores.id_proveedor'), nullable=False)   
    id_usuario_compras = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'), nullable=False)    
    

    usuario = db.relationship('Usuario', back_populates='compras')
    proveedor = db.relationship('Proveedor', back_populates='compras')
    detalle_compra = db.relationship('DetalleCompra', back_populates='compras')
    

    @staticmethod
    def get_compra(id_compra):
        return Compras.query.filter_by(id_compra=id_compra).first()
    
    classmethod
    def new(cls, kwargs):
        return Compras(**kwargs)    
    
    
    @staticmethod
    def get_compras():
        return Compras.query.all()
    
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
            print(f"Error al eliminar compra: {e}")
            return False
    
    @classmethod
    def insertar_compra(cls, data):
        """Llama al procedimiento almacenado usando extract_params para limpiar el código."""
        try:           
            query_params = Help.extract_params_compra(data, COLUMN_LIST_COMPRA)            
            query = text(INSERTAR_COMPRA)
            db.session.execute(query, query_params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al insertar compra: {e}")
            return False
    
    
    
