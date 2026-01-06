from flask import Blueprint, request
from ..models import Productos
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

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
@handle_endpoint_errors
def get_productos():
    try:
        productos = Productos.get_productos()
        return successfully(api_productos.dump(productos))
    except Exception as e:
        print(f"❌ Error obteniendo productos: {str(e)}")
        raise

@productos_routes.route('/producto', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Producto")
def post_producto():
    try:
        json = request.get_json(force=True)
        if not json:
            print(f"❌ JSON vacío en POST producto")
            return badRequest()
        producto = Productos.new(json)
        producto = Help.generator_id(producto, ID_PRODUCTO)
        if producto.save():
            print(f"✅ Producto creado con ID: {producto.id_producto}")
            return response(api_producto.dump(producto))
        print(f"❌ Error al guardar producto")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST producto: {str(e)}")
        raise

@productos_routes.route('/producto', methods=['GET'])
@set_productos_by()
def get_producto(producto):
    return successfully(api_producto.dump(producto))

@productos_routes.route('/producto', methods=['PUT'])
@set_productos_by()
@handle_endpoint_errors
@log_operation("Actualizar Producto")
def update_producto(producto):
    try:
        json = request.get_json(force=True)
        for key, value in json.items():
            setattr(producto, key, value)
        if producto.save():
            print(f"✅ Producto {producto.id_producto} actualizado")
            return update(api_producto.dump(producto))
        print(f"❌ Error al actualizar producto")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en PUT producto: {str(e)}")
        raise

@productos_routes.route('/producto', methods=['DELETE'])
@set_productos_by()
def delete_servicio(producto):
    if producto.delete():
        return delete()
    return badRequest()   