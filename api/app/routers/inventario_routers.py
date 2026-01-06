from flask import Blueprint, request
from ..models import Inventario
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

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
@handle_endpoint_errors
def get_inventarios():
    try:
        inventarios = Inventario.get_inventario_query()
        return successfully(api_inventarios.dump(inventarios))
    except Exception as e:
        print(f"❌ Error obteniendo inventarios: {str(e)}")
        raise

@inventario_routes.route('/inventario', methods=['POST'])
def post_inventario():
    json = request.get_json(force=True)
    inventario = Inventario.new(json)
    inventario = Help.generator_id(inventario, ID_INVENTARIO)
    if inventario.save():
        return response(api_inventario.dump(inventario))
    return badRequest()

@inventario_routes.route('/inventarioproducto', methods=['POST'])
@handle_endpoint_errors
@log_operation("Insertar Inventario Producto")
def post_inventario_producto():   
    try:
        data = request.get_json(force=True)    
        if not data:
            print(f"❌ Datos vacíos en POST inventarioproducto")
            return badRequest(ERROR)        
        if Inventario.insertar_inventario_producto(data):
            print(f"✅ Inventario producto insertado exitosamente")
            return response(SUCCESSFUL)        
        print(f"❌ Error al insertar inventario")
        return badEquals()
    except Exception as e:
        print(f"❌ Error en POST inventarioproducto: {str(e)}")
        raise
   

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
