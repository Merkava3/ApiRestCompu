from sqlalchemy import DateTime
from . import db
from .dispositivo_model import Dispositivo
from .cliente_model import Cliente

class Reparaciones(db.Model):
    __tablename__ = 'reparaciones'

    id_reparacion = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    dispositivo_id_reparacion = db.Column(db.BigInteger, db.ForeignKey('dispositivos.id_dispositivo'), nullable=False)
    estado = db.Column(db.String(45), nullable=False)   
    precio_reparacion = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_entrega = db.Column(DateTime, nullable=False)

    dispositivo = db.relationship('Dispositivo', back_populates='reparaciones')

    @staticmethod
    def get_reparacion(id_reparacion):
        return Reparaciones.query.filter_by(id_reparacion=id_reparacion).first()

    @staticmethod
    def get_reparaciones():
        return Reparaciones.query.all()
        
    @classmethod
    def new(cls, data):
        return cls(**data)

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
        
    @classmethod
    def get_reparaciones_con_clientes(cls):
        """
        Retorna las reparaciones con información del dispositivo y del cliente.
        """
        return db.session.query(
            Reparaciones.id_reparacion,
            Reparaciones.dispositivo_id_reparacion,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Reparaciones.precio_reparacion,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.numero_serie,
            Reparaciones.estado,
            Dispositivo.fecha_ingreso,
            Reparaciones.fecha_entrega
        ).join(Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo) \
         .join(Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente).all()
    
    @staticmethod
    def get_reparaciones_filter(cedula=None, numero_serie=None, id_reparacion=None):
        """
        Obtiene reparaciones filtrando por cédula, número de serie o ID de reparación.
        Si todos los valores son None, devuelve None.
        """
        query = db.session.query(
            Reparaciones.id_reparacion,
            Reparaciones.dispositivo_id_reparacion,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Reparaciones.precio_reparacion,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.numero_serie,
            Reparaciones.estado,
            Dispositivo.fecha_ingreso,
            Reparaciones.fecha_entrega
        ).join(
            Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo
        ).join(
            Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente
        )        
        if cedula is not None:
            query = query.filter(Cliente.cedula == cedula)
        if numero_serie is not None:
            query = query.filter(Dispositivo.numero_serie == numero_serie)
        if id_reparacion is not None:
            query = query.filter(Reparaciones.id_reparacion == id_reparacion)

        return query.first()
    
    @classmethod
    def get_reparaciones_completas(cls):
        """
        Retorna todas las reparaciones con información completa del dispositivo y del cliente.
        Incluye: id_reparacion, nombre_cliente, tipo, marca, modelo, reporte, numero_serie, estado, precio_reparacion, descripcion
        """
        return db.session.query(
            Reparaciones.id_reparacion,
            Cliente.nombre_cliente,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Reparaciones.estado,
            Reparaciones.precio_reparacion,
            Reparaciones.descripcion
        ).join(
            Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo
        ).join(
            Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente
        ).all()
    
    @staticmethod
    def get_reparacion_completa(id_reparacion):
        """
        Obtiene una reparación específica por ID con información completa del dispositivo y del cliente.
        Incluye: id_reparacion, nombre_cliente, tipo, marca, modelo, reporte, numero_serie, estado, precio_reparacion, descripcion
        """
        return db.session.query(
            Reparaciones.id_reparacion,
            Cliente.nombre_cliente,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Reparaciones.estado,
            Reparaciones.precio_reparacion,
            Reparaciones.descripcion
        ).join(
            Dispositivo, Reparaciones.dispositivo_id_reparacion == Dispositivo.id_dispositivo
        ).join(
            Cliente, Dispositivo.cliente_id_dispositivo == Cliente.id_cliente
        ).filter(
            Reparaciones.id_reparacion == id_reparacion
        ).first()