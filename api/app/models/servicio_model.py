import json
from sqlalchemy import *
from sqlalchemy.orm import joinedload
from .cliente_model import Cliente
from .dispositivo_model import Dispositivo
from .usuario_model import Usuario
from . import db
from .base_model import BaseModelMixin
from ..helpers.const import *
from ..helpers.helpers import Help


class Servicios(BaseModelMixin, db.Model):
    __tablename__ = 'servicios'
    
    id_servicio = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id_servicio = Column(Integer, ForeignKey('clientes.id_cliente'), nullable=False)
    dispositivo_id_servicio = Column(Integer, ForeignKey('dispositivos.id_dispositivo', ondelete='SET NULL'), nullable=True)
    usuario_id_servicio = Column(Integer, ForeignKey('usuarios.id_usuario'), nullable=False)
    tipo_servicio = Column(String(45), nullable=False)
    fecha_entrega = Column(DateTime, nullable=True)
    precio_servicio = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado_servicio = Column(Enum(*ESTADOS_SERVICIO, name='estado_servicio_enum'), nullable=False, default='recibido')
  

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='servicios')
    dispositivo = db.relationship('Dispositivo', back_populates='servicios')
    usuario = db.relationship('Usuario', back_populates='servicios')

    @staticmethod
    def _get_detailed_query():
        """
        Construye y retorna la consulta base detallada para servicios.
        Aplica DRY para get_servicio_all y get_servicio_filter.
        """
        dias_expr = (func.current_date() - cast(Dispositivo.fecha_ingreso, Date)).label("dias")
        
        return db.session.query(
            Servicios.id_servicio,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente,
            Servicios.tipo_servicio,
            Servicios.descripcion,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.tipo,
            Dispositivo.numero_serie,
            Servicios.estado_servicio,
            Dispositivo.reporte,
            Dispositivo.fecha_ingreso,
            Servicios.fecha_entrega,
            dias_expr,
            Servicios.precio_servicio,
            Usuario.email_usuario
        ).join(Usuario, Usuario.id_usuario == Servicios.usuario_id_servicio)\
         .join(Cliente, Cliente.id_cliente == Servicios.cliente_id_servicio)\
         .join(Dispositivo, Dispositivo.id_dispositivo == Servicios.dispositivo_id_servicio)

    @staticmethod
    def get_servicio_all():
        """Retorna todos los servicios con información detallada."""
        query = Servicios._get_detailed_query().order_by(Dispositivo.fecha_ingreso.desc())
        results = query.all()
        return Help.map_query_results(results, CAMPOS_SERVICIOS_COMPLETOS)
        
    @staticmethod
    def get_servicio_filter(cedula=None, id_servicio=None, many=False):
        """
        Retorna servicios filtrados con información completa.
        Busca por cedula o id_servicio.
        """
        query = Servicios._get_detailed_query()

        if id_servicio:
            query = query.filter(Servicios.id_servicio == id_servicio)
        elif cedula:
            query = query.filter(Cliente.cedula == cedula)
        elif not many:
            return None

        results = query.all()
        mapped_results = Help.map_query_results(results, CAMPOS_SERVICIOS_COMPLETOS)

        if many:
            return mapped_results
        return mapped_results[0] if mapped_results else None
    
    @staticmethod
    def get_ultimo_servicio():
        """
        Obtiene los últimos 10 servicios registrados basado en fecha de ingreso del dispositivo.
        Recrea la lógica SQL:
        ORDER BY d.fecha_ingreso DESC LIMIT 10
        """
        query = Servicios._get_detailed_query().order_by(Dispositivo.fecha_ingreso.desc()).limit(10)
        results = query.all()
        mapped_results = Help.map_query_results(results, CAMPOS_SERVICIOS_COMPLETOS)
        return mapped_results

    @staticmethod
    def get_servicio_by_cedula(cedula):
        """
        Obtiene el último servicio de un cliente por su cédula con columnas específicas.
        Recrea la consulta SQL solicitada.
        """
        query = db.session.query(
            Servicios.id_servicio,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente,
            Dispositivo.marca,
            Dispositivo.tipo,
            Servicios.estado_servicio,
            Dispositivo.fecha_ingreso,
            Servicios.precio_servicio,
            Usuario.email_usuario
        ).join(Usuario, Usuario.id_usuario == Servicios.usuario_id_servicio)\
         .join(Cliente, Cliente.id_cliente == Servicios.cliente_id_servicio)\
         .join(Dispositivo, Dispositivo.id_dispositivo == Servicios.dispositivo_id_servicio)\
         .filter(Cliente.cedula == cedula)\
         .order_by(Dispositivo.fecha_ingreso.desc())\
         .limit(1)
        
        result = query.first()
        
        if result:
            mapped = Help.map_query_results([result], CAMPOS_SERVICIOS_CEDULA)
            return mapped[0]
        return None
    
    @staticmethod
    def get_ultimo_servicio_detalle():
        """
        Obtiene el último servicio registrado con detalles completos.
        Recrea la consulta SQL solicitada.
        """
        query = db.session.query(
            Servicios.id_servicio,
            Usuario.email_usuario,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.direccion,
            Cliente.telefono_cliente,
            Dispositivo.tipo,
            Dispositivo.marca,
            Dispositivo.modelo,
            Dispositivo.numero_serie,
            Dispositivo.reporte,
            Dispositivo.fecha_ingreso,
            Servicios.tipo_servicio,
            Servicios.precio_servicio
        ).join(Usuario, Usuario.id_usuario == Servicios.usuario_id_servicio)\
         .join(Cliente, Cliente.id_cliente == Servicios.cliente_id_servicio)\
         .join(Dispositivo, Dispositivo.id_dispositivo == Servicios.dispositivo_id_servicio)\
         .order_by(Servicios.id_servicio.desc())\
         .limit(1)
        
        result = query.first()
        
        if result:
            mapped = Help.map_query_results([result], CAMPOS_SERVICIO_ULTIMO_DETALLE)
            return mapped[0]
        return None
    
    @staticmethod
    def get_servicio_reporte():
        """
        Obtiene el reporte de servicios con información de clientes y dispositivos.
        Retorna: id_servicio, cedula, nombre_cliente, telefono_cliente, fecha_ingreso, tipo_servicio
        """
        query = db.session.query(
            Servicios.id_servicio,
            Cliente.cedula,
            Cliente.nombre_cliente,
            Cliente.telefono_cliente,
            Dispositivo.fecha_ingreso,
            Servicios.tipo_servicio,
            Dispositivo.tipo,
            Dispositivo.reporte
        ).join(Usuario, Usuario.id_usuario == Servicios.usuario_id_servicio)\
         .join(Cliente, Cliente.id_cliente == Servicios.cliente_id_servicio)\
         .join(Dispositivo, Dispositivo.id_dispositivo == Servicios.dispositivo_id_servicio)
        
        results = query.all()
        
        if results:
            mapped = Help.map_query_results(results, CAMPOS_SERVICIO_REPORTE)
            return mapped
        return []
    
    @staticmethod
    def get_servicio_orm(id_servicio=None, cedula=None):
        """
        Retorna un objeto ORM de servicio para operaciones de actualización/eliminación.
        """
        query = Servicios.query.options(
            joinedload(Servicios.cliente),
            joinedload(Servicios.dispositivo),
            joinedload(Servicios.usuario)
        ).filter(Servicios.activo == True)

        if id_servicio:
            query = query.filter(Servicios.id_servicio == id_servicio)
        elif cedula:
            query = query.join(Cliente).filter(Cliente.cedula == cedula)
        
        return query.first()
    
    @classmethod
    def insertar_servicio(cls, data):
        """
        Llama al procedimiento almacenado sp_guardar_servicio_json.
        """
        try:
            Help.add_generated_id_to_data(data, ID_SERVICIO)
            clean_data = Help.extract_params_servicio_json(data)
            params = {'p_data': json.dumps(clean_data, ensure_ascii=False)}
            
            query = text(INSERTAR_SERVICIO_JSON)
            db.session.execute(query, params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al insertar servicio: {e}")
            raise e

    @classmethod
    def actualizar_servicio_completo(cls, data):
        """
        Llama al procedimiento almacenado sp_actualizar_servicio_json.
        """
        try:
            clean_data = Help.extract_params(data, list(COLUMN_LIST_ACTUALIZAR_SERVICIO), prefix="")
            params = {'p_data': json.dumps(clean_data, ensure_ascii=False)}
            
            query = text(ACTUALIZAR_SERVICIO_JSON)
            db.session.execute(query, params)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar servicio completo: {e}")
            raise e

    @classmethod
    def actualizar_fecha_entrega(cls, data):
        """
        Actualiza la fecha de entrega de un servicio al momento actual (NOW()).
        Recrea: UPDATE servicios SET fecha_entrega = NOW() WHERE id_servicio = :id;
        """
        try:
            id_servicio = data.get(ID_SERVICIO)
            if not id_servicio:
                return False

            # Usamos query.update para ser eficientes y directos, similar a la sentencia SQL bruta
            nrows = db.session.query(cls).filter(cls.id_servicio == id_servicio).update(
                {cls.fecha_entrega: func.now()},
                synchronize_session=False
            )
            
            db.session.commit()
            return nrows > 0
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar fecha entrega: {e}")
            return False