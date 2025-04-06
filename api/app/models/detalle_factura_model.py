from . import db

class DetalleFactura(db.Model):
    
    __tablename__ = 'detalle_factura'
    id_detalle_factura = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    factura_id_factura = db.Column(db.BigInteger, db.ForeignKey('facturas.id_factura'), nullable=False)
    producto_id_producto = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad_detalle = db.Column(db.Integer, nullable=False)
    sub_total = db.Column(db.Float, nullable=False)    
    
    factura = db.relationship('Facturas', back_populates='detalle_facturas')
    producto = db.relationship('Productos', back_populates='detalle_factura')
    

    @staticmethod
    def get_detalle_factura(id_detalle_factura):
        return DetalleFactura.query.filter_by(id_detalle_factura=id_detalle_factura).first()
    
    @staticmethod
    def get_detalle_facturas():
        return DetalleFactura.query.all()
    
    @classmethod
    def new(cls, kwargs):
        return DetalleFactura(**kwargs)
    
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
            print(f"Error al eliminar detalle_factura: {e}")
