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

    cliente = db.relationship('Cliente', back_populates='servicios')
    dispositivo = db.relationship('Dispositivo', back_populates='servicios')
    usuario = db.relationship('Usuario', back_populates='servicios')

    @staticmethod
    def _base_query():
        """Consulta base detallada."""
        dias_expr = (func.current_date() - cast(Dispositivo.fecha_ingreso, Date)).label("dias")
        return db.session.query(
            Servicios.id_servicio, Cliente.cedula, Cliente.nombre_cliente, Cliente.direccion,
            Cliente.telefono_cliente, Servicios.tipo_servicio, Servicios.descripcion,
            Dispositivo.marca, Dispositivo.modelo, Dispositivo.tipo, Dispositivo.numero_serie,
            Servicios.estado_servicio, Dispositivo.reporte, Dispositivo.fecha_ingreso,
            Servicios.fecha_entrega, dias_expr, Servicios.precio_servicio, Usuario.email_usuario
        ).join(Servicios.usuario).join(Servicios.cliente).join(Servicios.dispositivo)

    @staticmethod
    def get_servicio_all():
        """Todos los servicios ordenados por ingreso."""
        res = Servicios._base_query().order_by(Dispositivo.fecha_ingreso.desc()).all()
        return Help.map_query_results(res, CAMPOS_SERVICIOS_COMPLETOS)

    @staticmethod
    def get_servicio_filter(cedula=None, id_servicio=None, many=False):
        """Filtra servicios por cédula o ID."""
        q = Servicios._base_query()
        if id_servicio: q = q.filter(Servicios.id_servicio == id_servicio)
        elif cedula: q = q.filter(Cliente.cedula == cedula)
        elif not many: return None

        res = Help.map_query_results(q.all(), CAMPOS_SERVICIOS_COMPLETOS)
        return res if many else (res[0] if res else None)

    @staticmethod
    def get_ultimo_servicio():
        """Últimos 10 registrados."""
        res = Servicios._base_query().order_by(Dispositivo.fecha_ingreso.desc()).limit(10).all()
        return Help.map_query_results(res, CAMPOS_SERVICIOS_COMPLETOS)

    @staticmethod
    def get_servicio_by_cedula(cedula):
        """Último servicio de un cliente por cédula."""
        row = db.session.query(
            Servicios.id_servicio, Cliente.cedula, Cliente.nombre_cliente, Cliente.direccion,
            Cliente.telefono_cliente, Dispositivo.marca, Dispositivo.tipo, Servicios.estado_servicio,
            Dispositivo.fecha_ingreso, Servicios.precio_servicio, Usuario.email_usuario
        ).join(Servicios.usuario).join(Servicios.cliente).join(Servicios.dispositivo).filter(Cliente.cedula == cedula)\
         .order_by(Dispositivo.fecha_ingreso.desc()).first()
        return Help.map_query_results([row], CAMPOS_SERVICIOS_CEDULA)[0] if row else None

    @staticmethod
    def get_ultimo_servicio_detalle():
        """Detalle del último servicio."""
        row = db.session.query(
            Servicios.id_servicio, Usuario.email_usuario, Cliente.cedula, Cliente.nombre_cliente,
            Cliente.direccion, Cliente.telefono_cliente, Dispositivo.tipo, Dispositivo.marca,
            Dispositivo.modelo, Dispositivo.numero_serie, Dispositivo.reporte, Dispositivo.fecha_ingreso,
            Servicios.tipo_servicio, Servicios.precio_servicio
        ).join(Servicios.usuario).join(Servicios.cliente).join(Servicios.dispositivo)\
         .order_by(Dispositivo.fecha_ingreso.desc()).first()
        return Help.map_query_results([row], CAMPOS_SERVICIO_ULTIMO_DETALLE)[0] if row else None

    @staticmethod
    def get_servicio_reporte():
        """Reporte general de servicios."""
        res = db.session.query(
            Servicios.id_servicio, Cliente.cedula, Cliente.nombre_cliente, Cliente.telefono_cliente,
            Dispositivo.fecha_ingreso, Servicios.tipo_servicio, Dispositivo.tipo, Dispositivo.reporte
        ).join(Servicios.usuario).join(Servicios.cliente).join(Servicios.dispositivo).all()
        return Help.map_query_results(res, CAMPOS_SERVICIO_REPORTE) if res else []

    @staticmethod
    def get_servicios_tareas():
        """Servicios con estados activos."""
        res = db.session.query(
            Servicios.id_servicio, Dispositivo.fecha_ingreso, Cliente.nombre_cliente,
            Cliente.telefono_cliente, Dispositivo.tipo, Dispositivo.marca, Dispositivo.modelo,
            Dispositivo.reporte, Servicios.precio_servicio, Servicios.descripcion, Servicios.estado_servicio
        ).join(Servicios.cliente).join(Servicios.dispositivo).filter(Servicios.estado_servicio.in_(ESTADOS_SERVICIO_ACTIVOS))\
         .order_by(Dispositivo.fecha_ingreso.desc()).all()
        return Help.map_query_results(res, CAMPOS_SERVICIOS_TAREAS)

    @staticmethod
    def get_servicio_orm(id_servicio=None, cedula=None):
        """Objeto ORM para edición."""
        q = Servicios.query.options(joinedload(Servicios.cliente), joinedload(Servicios.dispositivo), joinedload(Servicios.usuario))
        if id_servicio: q = q.filter(Servicios.id_servicio == id_servicio)
        elif cedula: q = q.join(Cliente).filter(Cliente.cedula == cedula)
        return q.first()

    @classmethod
    def insertar_servicio(cls, data):
        """Guarda servicio usando sp_guardar_servicio_json."""
        try:
            Help.add_generated_id_to_data(data, ID_SERVICIO)
            params = {'p_data': json.dumps(Help.extract_params_servicio_json(data), ensure_ascii=False)}
            db.session.execute(text(INSERTAR_SERVICIO_JSON), params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def actualizar_servicio_completo(cls, data):
        """Actualiza servicio usando sp_actualizar_servicio_json."""
        try:
            params = {'p_data': json.dumps(Help.extract_params(data, list(COLUMN_LIST_ACTUALIZAR_SERVICIO), prefix=""), ensure_ascii=False)}
            db.session.execute(text(ACTUALIZAR_SERVICIO_JSON), params)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def actualizar_estado(cls, id_serv, estado, descripcion):
        """Actualiza el estado y la descripción del servicio."""
        if not Help.validate_status(estado, CAMPOS_TAREAS): return False
        try:
            res = cls.query.filter_by(id_servicio=id_serv).update({
                cls.estado_servicio: estado,
                cls.descripcion: descripcion
            })
            db.session.commit()
            return res > 0
        except:
            db.session.rollback()
            return False

    @classmethod
    def actualizar_fecha_entrega(cls, data):
        """Actualiza fecha de entrega a NOW()."""
        try:
            id_serv = data.get(ID_SERVICIO)
            if not id_serv: return False
            nrows = db.session.query(cls).filter(cls.id_servicio == id_serv).update({cls.fecha_entrega: func.now()}, synchronize_session=False)
            db.session.commit()
            return nrows > 0
        except Exception:
            db.session.rollback()
            return False
