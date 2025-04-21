from flask import Blueprint, request
from ..models.reparaciones_model import Reparaciones
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

reparacion_routes = Blueprint('reparacion_routes', __name__)

def set_reparacion_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_reparacion = json.get(ID_REPARACION)
            numero_serie = json.get(NUMERO_SERIE)
            cedula_cliente = json.get(CEDULA_CLIENT)
            reparacion = Reparaciones.get_reparacion(id_reparacion)
            if not reparacion:
                reparacion = Reparaciones.get_reparaciones_filter(cedula=cedula_cliente, numero_serie=numero_serie)           
            if not reparacion:
                return notFound()
            return function(reparacion, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@reparacion_routes.route('/reparaciones', methods=['GET'])
def get_reparaciones():
    reparaciones = Reparaciones.get_reparaciones_con_clientes()
    return successfully(api_reparaciones.dump(reparaciones))

@reparacion_routes.route('/reparacion', methods=['POST'])
def post_reparacion():
    json = request.get_json(force=True)
    reparacion = Reparaciones.new(json)
    reparacion = Help.generator_id(reparacion, ID_REPARACION)
    if reparacion.save():
        return response(api_reparacion.dump(reparacion))
    return badRequest()

@reparacion_routes.route('/reparacion', methods=['PUT'])
@set_reparacion_by()
def put_reparacion(reparacion):
    json = request.get_json(force=True)
    for key, value in json.items():
        setattr(reparacion, key, value)
    if reparacion.save():
        return update(api_cliente.dump(reparacion))      
    return badRequest()

@reparacion_routes.route('/reparacion', methods=['DELETE'])
@set_reparacion_by()
def delete_reparacion(reparacion):
    if reparacion.delete():
        return delete()
    return badRequest()

@reparacion_routes.route('/consulta/reparacion', methods=['GET'])
@set_reparacion_by()
def get_reparacion_cliente(reparacion):
    return successfully(api_reparaciones.dump(reparacion))
    