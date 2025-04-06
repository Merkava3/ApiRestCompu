from . import db

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id_proveedor = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nit = db.Column(db.String(16), nullable=False, unique=True)
    nombre_proveedor = db.Column(db.String(45), nullable=False)
    informacion_contacto = db.Column(db.Text, nullable=False)

    inventario = db.relationship('Inventario', back_populates='proveedor', lazy='dynamic')
    compras = db.relationship('Compras', back_populates='proveedor', lazy='dynamic')
    # Relación inversa con la tabla de productos

    @staticmethod
    def get_proveedor_id(id_proveedor):
        return Proveedor.query.filter_by(id_proveedor=id_proveedor).first()

    @staticmethod
    def get_proveedor_nit(nit):
        return Proveedor.query.filter_by(nit=nit).first()
    
    @staticmethod
    def get_proveedores():
        return Proveedor.query.all()
    
    @classmethod
    def new(cls, kwargs):
        return Proveedor(**kwargs)
    
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
            print(f"Error al eliminar proveedor: {e}")  # Para depuración
            return False