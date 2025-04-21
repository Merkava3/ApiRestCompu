from marshmallow import Schema, post_dump
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

class ServiciosSchemas(Schema):
    class Meta:
        fields = CAMPOS_SERVICIOS
        
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
    cliente = serializacion.Nested(ClienteSchemas)
    dispostivos = serializacion.Nested(Dispostivoschemas)
    servicio = serializacion.Nested(ServiciosSchemas)
    usuario = serializacion.Nested(UsuarioSchemas)
    class Meta:
        fields = columns_servicio_cliente 
    
    
    

# --- serialization cliente ----- 
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)

# --- serialization dispositivo ---
api_dispositivo  = Dispostivoschemas()
api_dispositivos = Dispostivoschemas(many=True)

# --- serialization reparaciones ---
api_reparacion = ReparacionesSchemas()
api_reparaciones = ReparacionesSchemas(many=True)

# --- serialization servicios ---
api_servicio = ServiciosSchemas()
api_servicios = ServiciosSchemas(many=True)
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