from flask import Blueprint, request
from ..models import Productos
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

productos_routes = Blueprint('productos_routes', __name__)

def set_productos_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_producto = json.get(ID_PRODUCTO)           
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if id_producto:
                producto = Productos.get_producto(id_producto)           
            if not producto:
                return notFound()
            return function(producto, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@productos_routes.route('/productos', methods=['GET'])
def get_productos():
    productos = Productos.get_productos()
    return successfully(api_productos.dump(productos))

@productos_routes.route('/producto', methods=['POST'])
def post_producto():
    json = request.get_json(force=True)
    producto = Productos.new(json)
    producto = Help.generator_id(producto, ID_PRODUCTO)
    if producto.save():
        return response(api_producto.dump(producto))
    return badRequest()

@productos_routes.route('/producto', methods=['GET'])
@set_productos_by()
def get_producto(producto):
    return successfully(api_producto.dump(producto))

@productos_routes.route('/producto', methods=['PUT'])
@set_productos_by()
def update_producto(producto):
    json = request.get_json(force=True)
    for key, value in json.items():
        setattr(producto, key, value)
    if producto.save():
        return update(api_producto.dump(producto))
    return badRequest()

@productos_routes.route('/producto', methods=['DELETE'])
@set_productos_by()
def delete_servicio(producto):
    if producto.delete():
        return delete()
    return badRequest()   