from flask import Blueprint, request
from ..models.cliente_model import Cliente
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..models.auth_decorator import token_required

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
def get_clients():
    clientes = Cliente.query.all()   
    return successfully(api_clientes.dump(clientes))
   
@cliente_routes.route('/cliente', methods=['GET'])
@set_client_by(CEDULA_CLIENT)
def get_client(cliente):
    return successfully(api_cliente.dump(cliente))

@cliente_routes.route('/cliente', methods=['POST'])
def post_client():
    json = request.get_json(force=True)
    cliente_exist = Cliente.get_cliente(json[CEDULA_CLIENT])
    if cliente_exist:
        return badEquals()
    else:
        device = Cliente.new(json)
        device = Help.generator_id(device, ID_CLIENTE)        
        if device.save():
            return response(api_cliente.dump(device))
    return badRequest()  

@cliente_routes.route('/cliente', methods=['PUT'])
@set_client_by(ID_CLIENTE)
def update_client(cliente):
    json = request.get_json(force=True)
    for key, value in json.items():
        setattr(cliente, key, value)
    if cliente.save():
        return update(api_cliente.dump(cliente))
    return badRequest()

@cliente_routes.route('/cliente', methods=['DELETE'])
@set_client_by(CEDULA_CLIENT)
def delete_client(cliente):
    if cliente.delete():
        return delete()
    return badRequest()

@cliente_routes.route('/clientes/count', methods=['GET'])
def count_clients():
    count = Cliente.count_clients()
    return successfully({"total_clients": count})

@cliente_routes.route('/clientes/ultimos', methods=['GET'])
def three_clients():
   theree= Cliente.get_last_three_clients()
   return successfully(api_clientes.dump(theree))