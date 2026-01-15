from flask import Blueprint, request
from ..models import Productos
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

productos_routes = Blueprint('productos_routes', __name__)

@productos_routes.route('/productos', methods=['GET'])
@handle_endpoint_errors
def get_productos():
    productos = Productos.get_productos()
    return successfully(api_productos.dump(productos))

@productos_routes.route('/producto', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Producto")
def post_producto():
    json = request.get_json(force=True)
    if not json:
        return badRequest()
    producto = Productos.new(json)
    producto = Help.generator_id(producto, ID_PRODUCTO)
    if producto.save():
        return response(api_producto.dump(producto))
    return badRequest()

@productos_routes.route('/producto', methods=['GET'])
@Help.set_resource(Productos.get_producto)
def get_producto(producto):
    return successfully(api_producto.dump(producto))

@productos_routes.route('/producto', methods=['PUT'])
@Help.set_resource(Productos.get_producto)
@handle_endpoint_errors
@log_operation("Actualizar Producto")
def update_producto(producto):
    json = request.get_json(force=True)
    producto.update_from_dict(json)
    if producto.save():
        return successfully(api_producto.dump(producto), "Registro Actualizado")
    return badRequest()

@productos_routes.route('/producto', methods=['DELETE'])
@Help.set_resource(Productos.get_producto)
def delete_servicio(producto):
    if producto.delete():
        return successfully(message="Registro eliminado")
    return badRequest()
