from . import db
class DetalleCompra(db.Model):
    __tablename__ = 'detalles_compras'
    id_detalle_compra = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    cantidad = db.Column(db.Integer, nullable=False)
    id_compras_detalles = db.Column(db.BigInteger, db.ForeignKey('compras.id_compras'), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    id_detalles_compras_productos = db.Column(db.BigInteger, db.ForeignKey('productos.id_producto'), nullable=False)

    compras = db.relationship('Compras', back_populates='detalle_compra')
    producto = db.relationship('Productos', back_populates='detalle_compra')
    

    @staticmethod
    def get_detalle_compra(id_detalle_compra):
        return DetalleCompra.query.filter_by(id_detalle_compra=id_detalle_compra).first()
    
    @staticmethod
    def get_detalle_compras():
        return DetalleCompra.query.all()
    
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
            print(f"Error al eliminar detalle_compra: {e}")
            return False
    
    @classmethod
    def new(cls, kwargs):
        return DetalleCompra(**kwargs)