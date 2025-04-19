from flask import Blueprint, request
from ..models import Inventario
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

inventario_routes = Blueprint('inventario_routes', __name__)

def set_inventario_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_inventario = json.get(ID_INVENTARIO) 
            id_producto = json.get(ID_PRODUCTO)         
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if id_inventario:
                inventario = Inventario.get_inventario(id_inventario)
            elif id_producto:                
                inventario = Inventario.get_inventario_by_producto(id_producto)                         
            if not inventario:
                return notFound()
            return function(inventario, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@inventario_routes.route('/inventarios', methods=['GET'])
def get_inventarios():
    inventarios = Inventario.get_inventario_query()
    return successfully(api_inventarios.dump(inventarios))

@inventario_routes.route('/inventario', methods=['POST'])
def post_inventario():
    json = request.get_json(force=True)
    inventario = Inventario.new(json)
    inventario = Help.generator_id(inventario, ID_INVENTARIO)
    if inventario.save():
        return response(api_inventario.dump(inventario))
    return badRequest()

@inventario_routes.route('/inventarioproducto', methods=['POST'])
def post_inventario_producto():   
    data = request.get_json(force=True)    
    if not data:
        return badRequest(ERROR)        
    if Inventario.insertar_inventario_producto(data):
        return response(SUCCESSFUL)        
    return badEquals()
   

@inventario_routes.route('/inventario', methods=['GET'])
@set_inventario_by()
def get_inventario(inventario):   
    if isinstance(inventario, list):
        return successfully(api_inventarios.dump(inventario))
    return notFound()

@inventario_routes.route('/inventario', methods=['PUT'])
@set_inventario_by()
def update_inventario(inventario):
    json = request.get_json(force=True)
    for key, value in json.items():
        setattr(inventario, key, value)
    if inventario.save():
        return update(api_inventario.dump(inventario))
    return badRequest()

@inventario_routes.route('/inventario', methods=['DELETE'])
@set_inventario_by()
def delete_inventario(inventario):
    if inventario.delete():
        return delete()
    return badRequest()
