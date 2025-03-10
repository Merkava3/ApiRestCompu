from marshmallow import Schema, post_dump
from marshmallow import fields as serializacion
from ..helpers.const import *

class ClienteSchemas(Schema):
    class Meta:
        fields = CAMPOS_CLIENTE
class DisoisitivoSchemas(Schema):
    class Meta:
        fields = CAMPOS_DISPOSITIVO

# --- serialization cliente ----- 
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)

# --- serialization dispositivo ---
api_dispositivo  = DisoisitivoSchemas()
api_dispositivos = DisoisitivoSchemas(many=True)
