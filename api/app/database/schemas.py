from marshmallow import Schema, EXCLUDE
from marshmallow import fields as serializacion
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..models import Cliente, Dispositivo, Servicios, Usuario
from ..helpers.const import *

# ======================== BASES (SOLID) ========================

class BaseAutoSchema(SQLAlchemyAutoSchema):
    """Esquema base para modelos SQLAlchemy."""
    class Meta:
        load_instance = True
        include_fk = True
        unknown = EXCLUDE

# ======================== MIXINS / COMPONENTES (DRY) ==========================

class ServiceMappedFields:
    """Campos calculados o aplanados para servicios."""
    # Mapeos dinámicos (Trabajan con objetos ORM)
    email_usuario = serializacion.Str(attribute="usuario.email_usuario", dump_only=True)
    nombre_usuario = serializacion.Str(attribute="usuario.nombre_usuario", dump_only=True)
    cedula = serializacion.Str(attribute="cliente.cedula", dump_only=True)
    nombre_cliente = serializacion.Str(attribute="cliente.nombre_cliente", dump_only=True)
    direccion = serializacion.Str(attribute="cliente.direccion", dump_only=True)
    telefono_cliente = serializacion.Str(attribute="cliente.telefono_cliente", dump_only=True)
    marca = serializacion.Str(attribute="dispositivo.marca", dump_only=True)
    modelo = serializacion.Str(attribute="dispositivo.modelo", dump_only=True)
    numero_serie = serializacion.Str(attribute="dispositivo.numero_serie", dump_only=True)
    tipo_dispositivo = serializacion.Str(attribute="dispositivo.tipo", dump_only=True)
    reporte = serializacion.Str(attribute="dispositivo.reporte", dump_only=True)
    
    # Formateo de fechas
    fecha_ingreso = serializacion.Function(
        lambda obj: (obj.dispositivo.fecha_ingreso if hasattr(obj, 'dispositivo') and obj.dispositivo else obj.fecha_ingreso if hasattr(obj, 'fecha_ingreso') else None).strftime('%d/%m/%Y') 
        if hasattr(obj, 'dispositivo') or hasattr(obj, 'fecha_ingreso') else None,
        dump_only=True
    )

# ======================== ESQUEMAS PRINCIPALES ========================

class ClienteSchemas(BaseAutoSchema):
    class Meta(BaseAutoSchema.Meta):
        model = Cliente
        fields = CAMPOS_CLIENTE

class Dispostivoschemas(BaseAutoSchema):
    cliente = serializacion.Nested(ClienteSchemas)
    # Aliases y aplanamiento
    descripcion = serializacion.Str(attribute="reporte")
    cedula = serializacion.Str(attribute="cliente.cedula", dump_only=True)
    nombre_cliente = serializacion.Str(attribute="cliente.nombre_cliente", dump_only=True)

    class Meta(BaseAutoSchema.Meta):
        model = Dispositivo
        fields = CAMPOS_DISPOSITIVO_CON_CLIENTE

class ServiciosSchemas(BaseAutoSchema, ServiceMappedFields):
    """Esquema estándar para el modelo Servicios."""
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIOS

class ServiciosUpdateSchemas(ServiciosSchemas):
    class Meta(ServiciosSchemas.Meta):
        fields = CAMPOS_SERVICIO_UPDATE

class ServiciosCompletosSchemas(BaseAutoSchema, ServiceMappedFields):
    """Esquema detallado con información de todas las relaciones."""
    # Campo calculado de días (disponible en queries custom)
    dias = serializacion.Raw(dump_only=True)
    
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIOS_COMPLETOS

class ServiciosCedulaSchemas(BaseAutoSchema, ServiceMappedFields):
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIOS_CEDULA

class UsuarioSchemas(BaseAutoSchema):
    class Meta(BaseAutoSchema.Meta):
        model = Usuario
        fields = CAMPOS_USUARIO

# ======================== ESQUEMAS AUXILIARES ========================

class SearchSchema(Schema):
    """Criterios de búsqueda."""
    id_servicio = serializacion.Raw(allow_none=True)
    cedula = serializacion.Str(allow_none=True)

    class Meta:
        unknown = EXCLUDE

class ServicioUltimoDetalleSchema(BaseAutoSchema, ServiceMappedFields):
    class Meta(BaseAutoSchema.Meta):
        model = Servicios
        fields = CAMPOS_SERVICIO_ULTIMO_DETALLE

class ServicioReporteSchema(Schema):
    """Reporte (Basado en Diccionarios)."""
    class Meta:
        fields = CAMPOS_SERVICIO_REPORTE
        unknown = EXCLUDE

class ServicioTareasSchema(Schema):
    """Tareas (Basado en Diccionarios)."""
    class Meta:
        fields = CAMPOS_SERVICIOS_TAREAS
        unknown = EXCLUDE

class ServicioUltimoResumenSchema(Schema):
    """Resumen (Basado en Diccionarios)."""
    class Meta:
        fields = CAMPOS_LISTA_ULTIMOS
        unknown = EXCLUDE

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
