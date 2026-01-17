from datetime import datetime
from . import db
from .dispositivo_model import Dispositivo
from .cliente_model import Cliente
from .usuario_model import Usuario
from .base_model import BaseModelMixin
from ..helpers.helpers import Help
from ..helpers.const import INSERTAR_SERVICIO, COLUMN_LIST_SERVICIO, ACTUALIZAR_SERVICIO_COMPLETO, COLUMN_LIST_ACTUALIZAR_SERVICIO
from sqlalchemy import text, func


class Servicios(BaseModelMixin, db.Model):
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

    @staticmethod
    def get_servicio_all():
        """
        Retorna todos los servicios con información de dispositivo, cliente y usuario pre-cargada.
        """
        from sqlalchemy.orm import joinedload
        return Servicios.query.options(
            joinedload(Servicios.cliente),
            joinedload(Servicios.dispositivos),
            joinedload(Servicios.usuario)
        ).all()
    
    @staticmethod
    def get_servicio_filter(cedula=None, numero_serie=None, id_servicio=None, many=False):
        """
        Retorna uno o varios objetos Servicio con información del dispositivo, cliente y usuario pre-cargada.
        """        
        from sqlalchemy.orm import joinedload
        query = Servicios.query.options(
            joinedload(Servicios.cliente),
            joinedload(Servicios.dispositivos),
            joinedload(Servicios.usuario)
        )

        if id_servicio:
            query = query.filter(Servicios.id_servicio == id_servicio)
        elif cedula:
            query = query.join(Cliente).filter(Cliente.cedula == cedula)
        elif numero_serie:
            query = query.join(Dispositivo).filter(Dispositivo.numero_serie == numero_serie)
        
        # Ordenar por fecha_servicio descendente (más nuevo primero)
        query = query.order_by(Servicios.fecha_servicio.desc())
        
        if many:
            return query.all()
        return query.first()
    
    @staticmethod
    def get_ultimo_servicio():
        """
        Retorna el último servicio insertado con información completa pre-cargada.
        """
        from sqlalchemy.orm import joinedload
        return Servicios.query.options(
            joinedload(Servicios.cliente),
            joinedload(Servicios.dispositivos),
            joinedload(Servicios.usuario)
        ).order_by(Servicios.fecha_servicio.desc(), Servicios.id_servicio.desc()) \
         .first()
    
    @staticmethod
    def insertar_servicio(data):
        """
        Llama al procedimiento almacenado usando extract_params para limpiar el código.
        """
        try:           
            query_params = Help.extract_params_servicio(data, COLUMN_LIST_SERVICIO)
            #print(f"Parámetros enviados al procedimiento almacenado - id_servicio: {query_params.get('p_id_servicio')}")  # Debug
            query = text(INSERTAR_SERVICIO)
            db.session.execute(query, query_params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al insertar servicio: {e}")
            return False

    @classmethod
    def actualizar_servicio_completo(cls, data):
        """
        Llama al procedimiento almacenado `actualizar_servicio_completo_json`.
        """
        try:
            # Mapeo de nombres alternativos a nombres esperados
            field_mapping = {
                'direccion': 'direccion_cliente',
                'marca': 'marca_dispositivo',
                'modelo': 'modelo_dispositivo',
                'reporte': 'reporte_dispositivo',
                'pago': 'pago_servicio',
                'precio': 'precio_servicio',
                'tipo': 'tipo_dispositivo',
                'cedula': 'cedula_cliente'
            }
            
            # Normalizar nombres de campos
            normalized_data = Help.normalize_field_names(data, field_mapping)
            
            # Extraer id_servicio
            id_servicio = normalized_data.get('id_servicio')
            if not id_servicio:
                # Intentar buscarlo en el payload original si no fue normalizado
                id_servicio = data.get('id_servicio')
            
            if not id_servicio:
                print("Error: id_servicio no proporcionado")
                return False

            # Eliminar campos que no se deben enviar al SP según requerimiento
            normalized_data.pop('fecha_ingreso', None)
            normalized_data.pop('fecha_servicio', None)

            # Preparar el JSON de datos (excluyendo id_servicio si se desea, 
            # aunque el procedimiento puede ignorarlo o usarlo)
            import json
            p_data = json.dumps(normalized_data)
            
            query = text(ACTUALIZAR_SERVICIO_COMPLETO)
            db.session.execute(query, {"p_id_servicio": id_servicio, "p_data": p_data})
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar servicio completo: {e}")
            return False

    @staticmethod
    def get_all_servicios_custom():
        """
        Ejecuta la consulta personalizada para obtener servicios con detalles específicos.
        """
        query_sql = """
            select 
                s.id_servicio,
                c.cedula,
                c.nombre_cliente,
                c.telefono_cliente,
                d.reporte,
                d.tipo,
                d.fecha_ingreso	 	
            from servicios as s 
                inner join dispositivos as d 
                    on d.id_dispositivo=s.dispositivos_id_servicio 
                inner join clientes as c 
                    on c.id_cliente = s.cliente_id_servicio;
        """
        try:
            result = db.session.execute(text(query_sql))
            return result.fetchall()
        except Exception as e:
            print(f"Error al ejecutar consulta personalizada: {e}")
            return []
