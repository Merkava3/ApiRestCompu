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
class ProductosSchemas(Schema):
    class Meta:
        fields = CAMPOS_PRODUCTOS

class ProveedorSchemas(Schema):
    class Meta:
        fields = CAMPOS_PROVEEDOR

class InventarioSchemas(Schema):
    class Meta:
        fields = CAMPOS_INVENTARIO

class SearchSchema(Schema):
    """Esquema para extraer criterios de búsqueda de las peticiones JSON."""
    id_servicio = serializacion.Raw(allow_none=True)   
    cedula = serializacion.Str(allow_none=True)
    
    class Meta:
        unknown = EXCLUDE

class FacturasSchemas(Schema):
    class Meta:
        fields = CAMPOS_FACTURAS

class DetalleFacturaSchemas(Schema):
    class Meta:
        fields = CAMPOS_DETALLE_FACTURA

class ComprasSchemas(Schema):
    class Meta:
        fields = CAMPOS_COMPRAS

class DetalleCompraSchemas(Schema):
    class Meta:
        fields = CAMPOS_DETALLE_COMPRA

class ServicioUltimoDetalleSchema(Schema):
    """Esquema para el último servicio con detalle específico."""
    class Meta:
        fields = CAMPOS_SERVICIO_ULTIMO_DETALLE

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

# --- serialization productos ---
api_producto = ProductosSchemas()
api_productos = ProductosSchemas(many=True)

# --- serialization proveedor ---
api_proveedor = ProveedorSchemas()
api_proveedores = ProveedorSchemas(many=True)

# --- serialization inventario ---
api_inventario = InventarioSchemas()
api_inventarios = InventarioSchemas(many=True)

# --- serialization ultimo servicio detalle ---
api_servicio_ultimo_detalle = ServicioUltimoDetalleSchema()