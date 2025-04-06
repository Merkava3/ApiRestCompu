from flask import Blueprint, request
from ..models import Facturas
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

facturas_routes = Blueprint('facturas_routes', __name__)

def set_facturas_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_factura = json.get(ID_FACTURA)            
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if id_factura:
                factura = Facturas.get_factura(id_factura)           
            if not factura:
                return notFound()
            return function(factura, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@facturas_routes.route('/factura', methods=['POST'])
def post_factura():
    data = request.get_json(force=True)    
    if not data:
        return badRequest(ERROR) 
       
    if Facturas.insertar_factura(data):
        return response(SUCCESSFUL)        
    return badEquals()