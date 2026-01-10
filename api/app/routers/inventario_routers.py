from flask import Blueprint, request
from ..models import Inventario
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation
from functools import wraps

inventario_routes = Blueprint('inventario_routes', __name__)

def set_inventario_by():
    """
    Decorador para inyectar el objeto o lista de inventario basado en ID_INVENTARIO o ID_PRODUCTO.
    """
    def decorator(function):
        @wraps(function)
        def wrap(*args, **kwargs):
            json = request.get_json(force=True) or {}
            id_inventario = json.get(ID_INVENTARIO) 
            id_producto = json.get(ID_PRODUCTO)         
            
            inventario = None
            # Buscar primero por ID de inventario específico
            if id_inventario:
                inventario = Inventario.get_inventario(id_inventario)
            # Luego intentar por ID de producto (puede retornar una lista)
            elif id_producto:                
                inventario = Inventario.get_inventario_by_producto(id_producto)                         
            
            if not inventario:
                return notFound()
                
            return function(inventario, *args, **kwargs)
        return wrap
    return decorator

@inventario_routes.route('/inventarios', methods=['GET'])
@handle_endpoint_errors
def get_inventarios():
    """Obtiene todos los registros de inventario con información detallada."""
    inventarios = Inventario.get_inventario_query()
    return successfully(api_inventarios.dump(inventarios))

@inventario_routes.route('/inventario', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Registro de Inventario")
def post_inventario():
    """Crea un nuevo registro de inventario."""
    json = request.get_json(force=True)
    if not json:
        return badRequest(ERROR)
        
    inventario = Inventario.new(json)
    inventario = Help.generator_id(inventario, ID_INVENTARIO)
    
    if inventario.save():
        return response(api_inventario.dump(inventario))
    return badRequest()

@inventario_routes.route('/inventarioproducto', methods=['POST'])
@handle_endpoint_errors
@log_operation("Insertar Inventario Producto (Procedimiento)")
def post_inventario_producto():   
    """Inserta inventario de producto usando procedimiento almacenado."""
    data = request.get_json(force=True)    
    if not data:
        return badRequest(ERROR)        
        
    if Inventario.insertar_inventario_producto(data):
        return response(SUCCESSFUL)        
    return badEquals()

@inventario_routes.route('/inventario', methods=['GET'])
@handle_endpoint_errors
@set_inventario_by()
def get_inventario(inventario):   
    """
    Obtiene uno o varios registros de inventario.
    Si se buscó por id_producto, inventario será una lista.
    Si se buscó por id_inventario, será un objeto individual.
    """
    if isinstance(inventario, list):
        return successfully(api_inventarios.dump(inventario))
    return successfully(api_inventario.dump(inventario))

@inventario_routes.route('/inventario', methods=['PUT'])
@handle_endpoint_errors
@log_operation("Actualizar Inventario")
@set_inventario_by()
def update_inventario(inventario):
    """Actualiza un registro de inventario específico."""
    if isinstance(inventario, list):
        return badRequest("Debe proporcionar un ID_INVENTARIO específico para actualizar, no un ID_PRODUCTO.")
        
    json = request.get_json(force=True)
    for key, value in json.items():
        if hasattr(inventario, key):
            setattr(inventario, key, value)
            
    if inventario.save():
        return update(api_inventario.dump(inventario))
    return badRequest()

@inventario_routes.route('/inventario', methods=['DELETE'])
@handle_endpoint_errors
@log_operation("Eliminar Inventario")
@set_inventario_by()
def delete_inventario(inventario):
    """Elimina un registro de inventario específico."""
    if isinstance(inventario, list):
        return badRequest("Debe proporcionar un ID_INVENTARIO específico para eliminar.")
        
    if inventario.delete():
        return delete()
    return badRequest()
