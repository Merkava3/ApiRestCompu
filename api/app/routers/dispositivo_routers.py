from flask import Blueprint, request
from ..models import Dispositivo
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

dispositivo_routes = Blueprint('dispositivo_routes', __name__)

def set_dispositivo_by(field):
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            value = json.get(field, None)
            if value is None:
                return notFound()
            dispositivo = (
                Dispositivo.get_dispositivo(value) if field == NUMERO_SERIE else  Dispositivo.get_id_dispositivo(value)
            )
            if dispositivo is None:
                return notFound()
            return function(dispositivo, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@dispositivo_routes.route('/dispositivos', methods=['GET'])
def get_dispositivos():
    dispositivo = Dispositivo.query.all()   
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

