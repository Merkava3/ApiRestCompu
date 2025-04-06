from . import db
from sqlalchemy import text
from datetime import datetime
from ..helpers.helpers import Help
from ..helpers.const import INSERTAR_FACTURA, COLUMN_LIST_FACTURA


class Facturas(db.Model):
    __tablename__ = 'facturas'
    id_factura = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    total = db.Column(db.Float, nullable=False)
    pago = db.Column(db.Float, nullable=False)
    factura_id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    fecha = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    id_cliente_facturas = db.Column(db.BigInteger, db.ForeignKey('clientes.id_cliente'), nullable=False)
    
    usuario = db.relationship('Usuario', back_populates='facturas')
    cliente = db.relationship('Cliente', back_populates='facturas')
    detalle_facturas = db.relationship('DetalleFactura', back_populates='factura')


    @staticmethod
    def get_factura(id_factura):
        return Facturas.query.filter_by(id_factura=id_factura).first()
    
    @staticmethod
    def get_facturas():
        return Facturas.query.all()
    
    @classmethod
    def new(cls, kwargs):
        return Facturas(**kwargs)
    
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
            print(f"Error al eliminar factura: {e}")

    @classmethod
    def insertar_factura(cls, data):
        """Llama al procedimiento almacenado usando extract_params para limpiar el código."""
        try:           
            query_params = Help.extract_params_factura(data, COLUMN_LIST_FACTURA)            
            query = text(INSERTAR_FACTURA)
            db.session.execute(query, query_params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al insertar factura: {e}")
            return False
   