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

# --- serialization cliente ----- 
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)

# --- serialization dispositivo ---
api_dispositivo  = Dispostivoschemas()
api_dispositivos = Dispostivoschemas(many=True)
