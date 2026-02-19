from marshmallow import Schema, EXCLUDE
from marshmallow import fields as serializacion
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Cliente, Dispositivo, Servicios, Usuario
from ..helpers.const import *

# ======================== BASES Y MIXINS (SOLID & DRY) ========================

class BaseAutoSchema(SQLAlchemyAutoSchema):
    """Esquema base para modelos SQLAlchemy."""
    class Meta:
        load_instance = True
        include_fk = True
        unknown = EXCLUDE

class ClientMappedMixin:
    """Campos aplanados de la relación Cliente."""
    cedula = serializacion.Str(attribute="cliente.cedula", dump_only=True)
    nombre_cliente = serializacion.Str(attribute="cliente.nombre_cliente", dump_only=True)
    direccion = serializacion.Str(attribute="cliente.direccion", dump_only=True)
    telefono_cliente = serializacion.Str(attribute="cliente.telefono_cliente", dump_only=True)

class DispositivoMappedMixin:
    """Campos aplanados de la relación Dispositivo."""
    marca = serializacion.Str(attribute="dispositivo.marca", dump_only=True)
    modelo = serializacion.Str(attribute="dispositivo.modelo", dump_only=True)
    numero_serie = serializacion.Str(attribute="dispositivo.numero_serie", dump_only=True)
    tipo_dispositivo = serializacion.Str(attribute="dispositivo.tipo", dump_only=True)
    reporte = serializacion.Str(attribute="dispositivo.reporte", dump_only=True)
    
    # Campo compartido para ingreso
    fecha_ingreso_formato = serializacion.Function(
        lambda obj: (obj.dispositivo.fecha_ingreso if hasattr(obj, 'dispositivo') and obj.dispositivo else None).strftime('%d/%m/%Y') 
        if hasattr(obj, 'dispositivo') and obj.dispositivo and obj.dispositivo.fecha_ingreso else None,
        dump_only=True
    )

class UsuarioMappedMixin:
    """Campos aplanados de la relación Usuario."""
    email_usuario = serializacion.Str(attribute="usuario.email_usuario", dump_only=True)
    nombre_usuario = serializacion.Str(attribute="usuario.nombre_usuario", dump_only=True)

# ======================== ESQUEMAS DE MODELOS ========================

class ClienteSchemas(BaseAutoSchema):
    class Meta(BaseAutoSchema.Meta):
        model = Cliente
        fields = CAMPOS_CLIENTE

class Dispostivoschemas(BaseAutoSchema, ClientMappedMixin):
    """Esquema para Dispositivo con información de Cliente."""
    cliente = serializacion.Nested(ClienteSchemas)
    # Aliases
    descripcion = serializacion.Str(attribute="reporte")
    
    class Meta(BaseAutoSchema.Meta):
        model = Dispositivo
        fields = CAMPOS_DISPOSITIVO_CON_CLIENTE

class ServiciosSchemas(BaseAutoSchema, ClientMappedMixin, DispositivoMappedMixin, UsuarioMappedMixin):
    """Esquema base para Servicios."""
    # Sobrescribimos fecha_ingreso de campos base si es necesario
    fecha_ingreso = serializacion.Function(
        lambda obj: obj.dispositivo.fecha_ingreso.strftime('%d/%m/%Y') 
        if hasattr(obj, 'dispositivo') and obj.dispositivo and obj.dispositivo.fecha_ingreso else None,
        dump_only=True
    )
    fecha_servicio = serializacion.Function(
        lambda obj: obj.fecha_servicio.strftime('%d/%m/%Y') 
        if hasattr(obj, 'fecha_servicio') and obj.fecha_servicio and not isinstance(obj.fecha_servicio, str) else obj.fecha_servicio,
        dump_only=True
    )

    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIOS

class ServiciosUpdateSchemas(ServiciosSchemas):
    class Meta(ServiciosSchemas.Meta):
        fields = CAMPOS_SERVICIO_UPDATE

class ServiciosCompletosSchemas(ServiciosSchemas):
    """Extensión para servicios detallados con días calculados."""
    dias = serializacion.Raw(dump_only=True)
    
    class Meta(ServiciosSchemas.Meta):
        fields = CAMPOS_SERVICIOS_COMPLETOS

class ServiciosCedulaSchemas(ServiciosSchemas):
    class Meta(ServiciosSchemas.Meta):
        fields = CAMPOS_SERVICIOS_CEDULA

class UsuarioSchemas(BaseAutoSchema):
    class Meta(BaseAutoSchema.Meta):
        model = Usuario
        fields = CAMPOS_USUARIO

# ======================== ESQUEMAS AUXILIARES / DICCIONARIOS ========================

class PlainSchema(Schema):
    """Base para esquemas que trabajan con diccionarios (Resultados de queries)."""
    class Meta:
        unknown = EXCLUDE

class SearchSchema(PlainSchema):
    id_servicio = serializacion.Raw(allow_none=True)
    cedula = serializacion.Str(allow_none=True)

class ServicioUltimoDetalleSchema(ServiciosSchemas):
    # Hereda mapeos pero usa campos específicos
    class Meta(ServiciosSchemas.Meta):
        fields = CAMPOS_SERVICIO_ULTIMO_DETALLE

class DictionaryFieldsMixin:
    """Declara campos comunes usados en esquemas de diccionario."""
    id_servicio = serializacion.Raw()
    cedula = serializacion.Str()
    nombre_cliente = serializacion.Str()
    telefono_cliente = serializacion.Str()
    fecha_ingreso = serializacion.Raw()
    tipo_servicio = serializacion.Str()
    tipo = serializacion.Str()
    reporte = serializacion.Str()
    marca = serializacion.Str()
    modelo = serializacion.Str()
    precio_servicio = serializacion.Raw()
    descripcion = serializacion.Str()
    estado_servicio = serializacion.Str()

class ServicioReporteSchema(PlainSchema, DictionaryFieldsMixin):
    class Meta(PlainSchema.Meta):
        fields = CAMPOS_SERVICIO_REPORTE

class ServicioTareasSchema(PlainSchema, DictionaryFieldsMixin):
    # Formateo especial para diccionarios
    fecha_ingreso = serializacion.Function(
        lambda obj: obj['fecha_ingreso'].strftime('%d/%m/%Y') 
        if isinstance(obj, dict) and obj.get('fecha_ingreso') and hasattr(obj['fecha_ingreso'], 'strftime') else obj.get('fecha_ingreso'),
        dump_only=True
    )
    class Meta(PlainSchema.Meta):
        fields = CAMPOS_SERVICIOS_TAREAS

class ServicioUltimoResumenSchema(PlainSchema, DictionaryFieldsMixin):
    class Meta(PlainSchema.Meta):
        fields = CAMPOS_LISTA_ULTIMOS

# ======================== INSTANCIAS (SINGLETONS) ========================

api_search = SearchSchema()
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)
api_dispositivo  = Dispostivoschemas()
api_dispositivos = Dispostivoschemas(many=True)
api_servicio = ServiciosSchemas()
api_servicios = ServiciosSchemas(many=True)
api_servicio_update = ServiciosUpdateSchemas()
api_servicios_completos = ServiciosCompletosSchemas(many=True)
api_servicio_completo = ServiciosCompletosSchemas()
api_servicio_cedula = ServiciosCedulaSchemas()
api_servicios_ultimo = ServicioUltimoResumenSchema(many=True)
api_usuario = UsuarioSchemas()
api_usuarios = UsuarioSchemas(many=True)
api_servicio_ultimo_detalle = ServicioUltimoDetalleSchema()
api_servicios_reporte = ServicioReporteSchema(many=True)
api_servicios_tareas = ServicioTareasSchema(many=True)
