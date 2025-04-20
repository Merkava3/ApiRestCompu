from flask import Blueprint, request
from ..models import Compras
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

compras_routes = Blueprint('compras_routes', __name__)

def set_compras_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_compra = json.get(ID_COMPRA)            
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if id_compra:
                compra = Compras.get_compra(id_compra)           
            if not compra:
                return notFound()
            return function(compra, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@compras_routes.route('/compras', methods=['POST'])
def post_compras():
    data = request.get_json(force=True)    
    if not data:
        return badRequest(ERROR)        
    if Compras.insertar_compra(data):
        return response(SUCCESSFUL)        
    return badEquals()


