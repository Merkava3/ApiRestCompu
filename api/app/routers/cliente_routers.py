from flask import Blueprint, request
from ..models.cliente_model import Cliente
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..models.auth_decorator import token_required
from ..helpers.error_handler import handle_endpoint_errors, log_operation

cliente_routes = Blueprint('cliente_routes', __name__)

def set_client_by(field):
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            value = json.get(field, None)
            if value is None:
                return notFound()
            cliente = (
                Cliente.get_cliente(value) if field == CEDULA_CLIENT else Cliente.get_id_client(value)
            )
            if cliente is None:
                return notFound()
            return function(cliente, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@cliente_routes.route('/clientes', methods=['GET'])
@token_required
@handle_endpoint_errors
def get_clients():
    try:
        clientes = Cliente.query.all()   
        return successfully(api_clientes.dump(clientes))
    except Exception as e:
        print(f"❌ Error obteniendo clientes: {str(e)}")
        raise
   
@cliente_routes.route('/cliente', methods=['GET'])
@set_client_by(CEDULA_CLIENT)
def get_client(cliente):
    return successfully(api_cliente.dump(cliente))

@cliente_routes.route('/cliente', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Cliente")
def post_client():
    try:
        json = request.get_json(force=True)
        if not json:
            print(f"❌ JSON vacío en POST cliente")
            return badRequest()
        cliente_exist = Cliente.get_cliente(json.get(CEDULA_CLIENT))
        if cliente_exist:
            print(f"⚠️  Cliente con cédula {json.get(CEDULA_CLIENT)} ya existe")
            return badEquals()
        device = Cliente.new(json)
        device = Help.generator_id(device, ID_CLIENTE)        
        if device.save():
            print(f"✅ Cliente creado con ID: {device.id_cliente}")
            return response(api_cliente.dump(device))
        print(f"❌ Error al guardar cliente")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST cliente: {str(e)}")
        raise  

@cliente_routes.route('/cliente', methods=['PUT'])
@set_client_by(ID_CLIENTE)
@handle_endpoint_errors
@log_operation("Actualizar Cliente")
def update_client(cliente):
    try:
        json = request.get_json(force=True)
        for key, value in json.items():
            setattr(cliente, key, value)
        if cliente.save():
            print(f"✅ Cliente {cliente.id_cliente} actualizado")
            return update(api_cliente.dump(cliente))
        print(f"❌ Error al actualizar cliente {cliente.id_cliente}")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en PUT cliente: {str(e)}")
        raise

@cliente_routes.route('/cliente', methods=['DELETE'])
@set_client_by(CEDULA_CLIENT)
@handle_endpoint_errors
@log_operation("Eliminar Cliente")
def delete_client(cliente):
    try:
        if cliente.delete():
            print(f"✅ Cliente {cliente.id_cliente} eliminado")
            return delete()
        print(f"❌ Error al eliminar cliente {cliente.id_cliente}")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en DELETE cliente: {str(e)}")
        raise

@cliente_routes.route('/clientes/count', methods=['GET'])
def count_clients():
    count = Cliente.count_clients()
    return successfully({"total_clients": count})

@cliente_routes.route('/clientes/ultimos', methods=['GET'])
def three_clients():
   theree= Cliente.get_last_three_clients()
   return successfully(api_clientes.dump(theree))