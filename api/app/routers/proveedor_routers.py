from flask import Blueprint, request
from ..models import Proveedor
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

proveedor_routes = Blueprint('proveedor_routes', __name__)

def set_proveedor_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_proveedor = json.get(ID_PROVEEDOR)
            nit = json.get(NIT)
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if id_proveedor:
                proveedor = Proveedor.get_proveedor_id(id_proveedor)
            if nit:
                proveedor = Proveedor.get_proveedor_nit(nit)
            if not proveedor:
                return notFound()
            return function(proveedor, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@proveedor_routes.route('/proveedores', methods=['GET'])
@handle_endpoint_errors
def get_proveedores():
    try:
        proveedores = Proveedor.get_proveedores()
        return successfully(api_proveedores.dump(proveedores))
    except Exception as e:
        print(f"❌ Error obteniendo proveedores: {str(e)}")
        raise

@proveedor_routes.route('/proveedor', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Proveedor")
def post_proveedor():
    try:
        json = request.get_json(force=True)
        if not json:
            print(f"❌ JSON vacío en POST proveedor")
            return badRequest()
        proveedor = Proveedor.new(json)
        proveedor = Help.generator_id(proveedor, ID_PROVEEDOR)
        if proveedor.save():
            print(f"✅ Proveedor creado con ID: {proveedor.id_proveedor}")
            return response(api_proveedor.dump(proveedor))
        print(f"❌ Error al guardar proveedor")
        return badEquals()
    except Exception as e:
        print(f"❌ Error en POST proveedor: {str(e)}")
        raise

@proveedor_routes.route('/proveedor', methods=['GET'])
@set_proveedor_by()
def get_proveedor(proveedor):
    return successfully(api_proveedor.dump(proveedor))

@proveedor_routes.route('/proveedor', methods=['PUT'])
@set_proveedor_by()
@handle_endpoint_errors
@log_operation("Actualizar Proveedor")
def update_proveedor(proveedor):
    try:
        json = request.get_json(force=True)
        for key, value in json.items():
            setattr(proveedor, key, value)
        if proveedor.save():
            print(f"✅ Proveedor {proveedor.id_proveedor} actualizado")
            return update(api_proveedor.dump(proveedor))
        print(f"❌ Error al actualizar proveedor")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en PUT proveedor: {str(e)}")
        raise

@proveedor_routes.route('/proveedor', methods=['DELETE'])
@set_proveedor_by()
def delete_proveedor(proveedor):
    if proveedor.delete():
        return delete()
    return badRequest()



