from marshmallow import Schema, post_dump, EXCLUDE
from marshmallow import fields as serializacion
from ..helpers.const import *

class ClienteSchemas(Schema):
    class Meta:
        fields = CAMPOS_CLIENTE
        
class Dispostivoschemas(Schema):
    cliente = serializacion.Nested(ClienteSchemas)
    class Meta:
        fields = CAMPOS_DISPOSITIVO_CON_CLIENTE

class ReparacionesSchemas(Schema):
    class Meta:
        fields = CAMPOS_REPARACIONES

class ReparacionesCompletasSchemas(Schema):
    class Meta:
        fields = CAMPOS_REPARACIONES_COMPLETAS

class ServiciosSchemas(Schema):
    # Fechas formateadas (Lógica especial)
    fecha_ingreso = serializacion.Function(lambda obj: obj.dispositivos.fecha_ingreso.strftime('%d/%m/%Y') if hasattr(obj, 'dispositivos') and obj.dispositivos and obj.dispositivos.fecha_ingreso else (obj.fecha_ingreso if hasattr(obj, 'fecha_ingreso') else None))
    fecha_servicio = serializacion.Function(lambda obj: obj.fecha_servicio.strftime('%d/%m/%Y') if hasattr(obj, 'fecha_servicio') and obj.fecha_servicio and not isinstance(obj.fecha_servicio, str) else (obj.fecha_servicio if hasattr(obj, 'fecha_servicio') else None))

    class Meta:
        fields = CAMPOS_SERVICIOS

class ServiciosUpdateSchemas(ServiciosSchemas):
    class Meta:
        fields = CAMPOS_SERVICIO_UPDATE

# Registro de campos dinámicos para aplanamiento (DRY)
# Se añaden a _declared_fields para que Marshmallow los reconozca al instanciar
for field_name, attr_path in MAPEO_ATRIBUTOS_SERVICIO.items():
    if 'fecha' not in field_name:
        ServiciosSchemas._declared_fields[field_name] = serializacion.Str(attribute=attr_path)
        
class UsuarioSchemas(Schema):
    class Meta:
        fields = CAMPOS_USUARIO
class ProductosSchemas(Schema):
    class Meta:
        fields = CAMPOS_PRODUCTOS

class ProveedorSchemas(Schema):
    class Meta:
        fields = CAMPOS_PROVEEDOR

class InventarioSchemas(Schema):
    class Meta:
        fields = CAMPOS_INVENTARIO

class ServicioClientesSchemas(Schema):
    class Meta:
        fields = columns_servicio_cliente 

class SearchSchema(Schema):
    """Esquema para extraer criterios de búsqueda de las peticiones JSON."""
    id_servicio = serializacion.Raw(allow_none=True)
    id_reparacion = serializacion.Raw(allow_none=True)
    numero_serie = serializacion.Str(allow_none=True)
    cedula = serializacion.Str(allow_none=True)
    
    class Meta:
        fields = CAMPOS_BUSQUEDA
        unknown = EXCLUDE

# --- serialization cliente ----- 
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)

# --- serialization dispositivo ---
api_dispositivo  = Dispostivoschemas()
api_dispositivos = Dispostivoschemas(many=True)

# --- serialization reparaciones ---
api_reparacion = ReparacionesSchemas()
api_reparaciones = ReparacionesSchemas(many=True)
api_reparacion_completa = ReparacionesCompletasSchemas()
api_reparaciones_completas = ReparacionesCompletasSchemas(many=True)

# --- serialization servicios ---
api_servicio = ServiciosSchemas()
api_servicios = ServiciosSchemas(many=True)
api_servicio_update = ServiciosUpdateSchemas()
api_servicio_cliente = ServicioClientesSchemas(many=True)

# --- serialization usuario ---
api_usuario = UsuarioSchemas()
api_usuarios = UsuarioSchemas(many=True)

# --- serialization productos ---
api_producto = ProductosSchemas()
api_productos = ProductosSchemas(many=True)

# --- serialization proveedor ---
api_proveedor = ProveedorSchemas()
api_proveedores = ProveedorSchemas(many=True)

# --- serialization inventario ---
api_inventario = InventarioSchemas()
api_inventarios = InventarioSchemas(many=True)

# --- search schema ---
api_search = SearchSchema()

class ServicioConsultaSchemas(Schema):
    fecha_ingreso = serializacion.Function(lambda obj: obj.fecha_ingreso.strftime('%d/%m/%Y') if obj.fecha_ingreso else None)
    class Meta:
        fields = CAMPOS_CONSULTA_SERVICIO

api_servicio_consulta = ServicioConsultaSchemas(many=True)