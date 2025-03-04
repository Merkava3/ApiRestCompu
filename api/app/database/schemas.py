from marshmallow import Schema, post_dump
from marshmallow import fields as serializacion
from ..helpers.const import *

class ClienteSchemas(Schema):
    class Meta:
        fields = CAMPOS_CLIENTE

# --- serialization cliente ----- 
api_cliente  = ClienteSchemas()
api_clientes = ClienteSchemas(many=True)
