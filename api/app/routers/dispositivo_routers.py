from flask import Blueprint, request
from ..models import Dispositivo
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

dispositivo_routes = Blueprint('dispositivo_routes', __name__)

def set_dispositivo_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_dispositivo = json.get(ID_DISPOSITIVO)
            numero_serie = json.get(NUMERO_SERIE)
            cedula_cliente = json.get(CEDULA_CLIENT)
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if id_dispositivo:
                dispositivo = Dispositivo.get_id_dispositivo(id_dispositivo)
            else:               
                dispositivo = Dispositivo.get_dispositivo_filter(cedula=cedula_cliente, numero_serie=numero_serie)
            if not dispositivo:
                return notFound()
            
            return function(dispositivo, *args, **kwargs)

        wrap.__name__ = function.__name__
        return wrap
    return decorator

@dispositivo_routes.route('/dispositivos', methods=['GET'])
def get_dispositivos():
    dispositivo = Dispositivo.get_dispositivos_con_clientes() 
    return successfully(api_dispositivos.dump(dispositivo))

@dispositivo_routes.route('/dispositivo', methods=['POST'])
def post_dispositivo():
    json = request.get_json(force=True)
    dispositivo_exist = Dispositivo.get_dispositivo(json[NUMERO_SERIE])
    if dispositivo_exist:
        return badEquals()
    else:
        device = Dispositivo.new(json)
        device = Help.generator_id(device, ID_DISPOSITIVO)        
        if device.save():
            return response(api_dispositivo.dump(device))
    return badRequest()

@dispositivo_routes.route('/dispositivo', methods=['GET'])
@set_dispositivo_by()
def get_dispositivo(dispositivo):  
    return successfully(api_dispositivo.dump(dispositivo))

@dispositivo_routes.route('/IDdispositivo', methods=['GET'])
@set_dispositivo_by()
def get_id_dispositivo(dispositivo):  
    return successfully(api_dispositivo.dump(dispositivo))

@dispositivo_routes.route('/dispositivo', methods=['DELETE'])
@set_dispositivo_by()
def delete_dispositivo(dispositivo):
    if dispositivo.delete():
        return delete()
    return badRequest()

@dispositivo_routes.route('/dispositivo', methods=['PUT'])
@set_dispositivo_by()
def update_client(dispositivo):
    json = request.get_json(force=True)
    for key, value in json.items():
        setattr(dispositivo, key, value)
    if dispositivo.save():
        return update(api_dispositivo.dump(dispositivo))
    return badRequest()