from flask import Blueprint, request
from ..models.cliente_model import Cliente
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..models.auth_decorator import token_required
from ..helpers.error_handler import handle_endpoint_errors, log_operation

cliente_routes = Blueprint('cliente_routes', __name__)

@cliente_routes.route('/clientes', methods=['GET'])
@token_required
@handle_endpoint_errors
def get_clients():
    clientes = Cliente.query.all()   
    return successfully(api_clientes.dump(clientes))
   
@cliente_routes.route('/cliente', methods=['GET'])
@Help.set_resource(Cliente.get_cliente)
def get_client(cliente):
    return successfully(api_cliente.dump(cliente))

@cliente_routes.route('/cliente', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Cliente")
def post_client():
    json = request.get_json(force=True)
    if not json:
        return badRequest()
    cliente_exist = Cliente.get_cliente(json.get(CEDULA_CLIENT))
    if cliente_exist:
        return badEquals()
    device = Cliente.new(json)
    device = Help.generator_id(device, ID_CLIENTE)        
    if device.save():
        return response(api_cliente.dump(device))
    return badRequest()  

@cliente_routes.route('/cliente', methods=['PUT'])
@Help.set_resource(Cliente.get_id_client)
@handle_endpoint_errors
@log_operation("Actualizar Cliente")
def update_client(cliente):
    json = request.get_json(force=True)
    cliente.update_from_dict(json)
    if cliente.save():
        return successfully(api_cliente.dump(cliente), "Registro Actualizado")
    return badRequest()

@cliente_routes.route('/cliente', methods=['DELETE'])
@Help.set_resource(Cliente.get_cliente)
@handle_endpoint_errors
@log_operation("Eliminar Cliente")
def delete_client(cliente):
    if cliente.delete():
        return successfully(message="Registro eliminado")
    return badRequest()

@cliente_routes.route('/clientes/count', methods=['GET'])
def count_clients():
    count = Cliente.count_clients()
    return successfully({"total_clients": count})

@cliente_routes.route('/clientes/ultimos', methods=['GET'])
def three_clients():
   theree= Cliente.get_last_three_clients()
   return successfully(api_clientes.dump(theree))
