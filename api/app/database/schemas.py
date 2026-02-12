from marshmallow import Schema, EXCLUDE
from marshmallow import fields as serializacion
from ..helpers.const import *

class ClienteSchemas(Schema):
    class Meta:
        fields = CAMPOS_CLIENTE

class Dispostivoschemas(Schema):
    cliente = serializacion.Nested(ClienteSchemas)
    class Meta:
        fields = CAMPOS_DISPOSITIVO_CON_CLIENTE

class ServiciosSchemas(Schema):
    # Fechas formateadas (Lógica especial)
    fecha_ingreso = serializacion.Function(lambda obj: obj.dispositivo.fecha_ingreso.strftime('%d/%m/%Y') if hasattr(obj, 'dispositivo') and obj.dispositivo and obj.dispositivo.fecha_ingreso else (obj.fecha_ingreso if hasattr(obj, 'fecha_ingreso') else None))
    fecha_servicio = serializacion.Function(lambda obj: obj.fecha_servicio.strftime('%d/%m/%Y') if hasattr(obj, 'fecha_servicio') and obj.fecha_servicio and not isinstance(obj.fecha_servicio, str) else (obj.fecha_servicio if hasattr(obj, 'fecha_servicio') else None))

    class Meta:
        fields = CAMPOS_SERVICIOS

class ServiciosUpdateSchemas(ServiciosSchemas):
    class Meta:
        fields = CAMPOS_SERVICIO_UPDATE

class ServiciosCompletosSchemas(Schema):
    """Esquema para servicios con consulta personalizada que incluye info de clientes, dispositivos y usuarios."""
    class Meta:
        fields = CAMPOS_SERVICIOS_COMPLETOS

class ServiciosCedulaSchemas(Schema):
    """Esquema específico para búsqueda por cédula con campos reducidos."""
    class Meta:
        fields = CAMPOS_SERVICIOS_CEDULA

# Registro de campos dinámicos para aplanamiento (DRY)
# Se añaden a _declared_fields para que Marshmallow los reconozca al instanciar
for field_name, attr_path in MAPEO_ATRIBUTOS_SERVICIO.items():
    if 'fecha' not in field_name:
        ServiciosSchemas._declared_fields[field_name] = serializacion.Str(attribute=attr_path)

class UsuarioSchemas(Schema):
    class Meta:
        fields = CAMPOS_USUARIO
class SearchSchema(Schema):
    """Esquema para extraer criterios de búsqueda de las peticiones JSON."""
    id_servicio = serializacion.Raw(allow_none=True)
    cedula = serializacion.Str(allow_none=True)

    class Meta:
        unknown = EXCLUDE

class ServicioUltimoDetalleSchema(Schema):
    """Esquema para el último servicio con detalle específico."""
    class Meta:
        fields = CAMPOS_SERVICIO_ULTIMO_DETALLE

class ServicioReporteSchema(Schema):
    """Esquema para reporte de servicios."""
    class Meta:
        fields = CAMPOS_SERVICIO_REPORTE

class ServicioTareasSchema(Schema):
    """Esquema para tareas de servicios con información de clientes y dispositivos."""
    # Fecha formateada para mejor legibilidad
    fecha_ingreso = serializacion.Function(lambda obj: obj['fecha_ingreso'].strftime('%d/%m/%Y') if obj.get('fecha_ingreso') and hasattr(obj['fecha_ingreso'], 'strftime') else obj.get('fecha_ingreso'))

    class Meta:
        fields = CAMPOS_SERVICIOS_TAREAS

# --- search schema ---
api_search = SearchSchema()

# --- serialization cliente -----
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)

# --- serialization dispositivo ---
api_dispositivo  = Dispostivoschemas()
api_dispositivos = Dispostivoschemas(many=True)

# --- serialization servicios ---
api_servicio = ServiciosSchemas()
api_servicios = ServiciosSchemas(many=True)
api_servicio_update = ServiciosUpdateSchemas()
api_servicios_completos = ServiciosCompletosSchemas(many=True)
api_servicio_completo = ServiciosCompletosSchemas()
api_servicio_cedula = ServiciosCedulaSchemas()

# --- serialization usuario ---
api_usuario = UsuarioSchemas()
api_usuarios = UsuarioSchemas(many=True)

# --- serialization ultimo servicio detalle ---
api_servicio_ultimo_detalle = ServicioUltimoDetalleSchema()

# --- serialization reporte servicios ---
api_servicios_reporte = ServicioReporteSchema(many=True)

# --- serialization tareas servicios ---
api_servicios_tareas = ServicioTareasSchema(many=True)
