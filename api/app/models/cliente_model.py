from sqlalchemy import Column, Integer, String, Text
from . import db 

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    cedula = Column(String(16), nullable=False, unique=True)
    nombre_cliente = Column(String(255), nullable=False)
    direccion = Column(Text, nullable=False)
    telefono_cliente = Column(String(50))

    @staticmethod
    def get_cliente(cedula):
        return Cliente.query.filter_by(cedula=cedula).first()
    
    @staticmethod
    def get_id_client(id_cliente):
        return Cliente.query.filter_by(id_cliente=id_cliente).first()
    
    @classmethod
    def count_clients(cls):
        return db.session.query(db.func.count(cls.cedula)).scalar()
    
    @classmethod
    def get_last_three_clients(cls):      
        return cls.query.order_by(cls.cedula.desc()).limit(3).all()

    @classmethod
    def new(cls, kwargs):
        return Cliente(**kwargs)

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
        except:
            return False