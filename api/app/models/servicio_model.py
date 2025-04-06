from datetime import datetime
from . import db
from .dispositivo_model import Dispositivo
from .cliente_model import Cliente
from .usuario_model import Usuario

class Servicios(db.Model):
    __tablename__ = 'servicios'  # Nombre de la tabla

    id_servicio = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    cliente_id_servicio = db.Column(db.BigInteger, db.ForeignKey('clientes.id_cliente'), nullable=False)
    dispositivos_id_servicio = db.Column(db.BigInteger, db.ForeignKey('dispositivos.id_dispositivo'), nullable=False)
    usuario_id_servicio = db.Column(db.BigInteger, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    tipo = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(45), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)    
    fecha_servicio = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
    pago = db.Column(db.Float, nullable=False)
    precio_servicio = db.Column(db.Float, nullable=False)

    cliente = db.relationship('Cliente', back_populates='servicios')
    dispositivos = db.relationship('Dispositivo', back_populates='servicios')
    usuario = db.relationship('Usuario', back_populates='servicios')

    @staticmethod
    def get_servicio(id_servicio):
        return Servicios.query.filter_by(id_servicio=id_servicio).first()

    @classmethod
    def new(cls, kwargs):  # Convierte un diccionario en un objeto Servicios
        return Servicios(**kwargs)
    
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
            print(f"Error al eliminar servicio: {e}")  # Para depuración
            return False
            
    @staticmethod
    def get_servicio_all():
        return db.session.query(
            Servicios.id_servicio,
            Usuario.email_usuario,
            Usuario.nombre_usuario,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Dispositivo.fecha_ingreso,
            Servicios.fecha_servicio,
            Dispositivo.tipo.label("tipo_dispositivo"),
            Servicios.tipo.label("tipo_servicio"),
            Servicios.pago,
            Servicios.precio_servicio
        ).join(Usuario, Servicios.usuario_id_servicio == Usuario.id_usuario) \
         .join(Cliente, Servicios.cliente_id_servicio == Cliente.id_cliente) \
         .join(Dispositivo, Servicios.dispositivos_id_servicio == Dispositivo.id_dispositivo) \
         .all()
    
    @staticmethod
    def get_servicio_filter(cedula=None, numero_serie=None, id_servicio=None):
        """
        Retorna los servicios con información del dispositivo, cliente y usuario.
        """        
        query = db.session.query(
            Servicios.id_servicio,
            Servicios.estado,
            Usuario.email_usuario,
            Usuario.nombre_usuario,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.reporte,
            Dispositivo.numero_serie,
            Dispositivo.fecha_ingreso,
            Servicios.fecha_servicio,
            Dispositivo.tipo.label("tipo_dispositivo"),
            Servicios.tipo.label("tipo_servicio"),
            Servicios.pago,
            Servicios.precio_servicio
        ).join(Usuario, Servicios.usuario_id_servicio == Usuario.id_usuario) \
         .join(Cliente, Servicios.cliente_id_servicio == Cliente.id_cliente) \
         .join(Dispositivo, Servicios.dispositivos_id_servicio == Dispositivo.id_dispositivo)
        if cedula:
            query = query.filter(Cliente.cedula == cedula)
        if numero_serie:
            query = query.filter(Dispositivo.numero_serie == numero_serie)
        if id_servicio:
            query = query.filter(Servicios.id_servicio == id_servicio)
        resultado = query.first()
        return resultado