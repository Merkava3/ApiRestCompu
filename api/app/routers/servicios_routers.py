from flask import Blueprint, request
from ..models import Servicios
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

servicios_routes = Blueprint('servicios_routes', __name__)

def set_servicios_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_servicio = json.get(ID_SERVICIO)
            numero_serie = json.get(NUMERO_SERIE)
            cedula_cliente = json.get(CEDULA_CLIENT)          
            # Buscar primero por ID, luego por Número de Serie o Cédula           
            if id_servicio:                              
                servicio = Servicios.get_servicio(id_servicio)
            else:                                 
                servicio = Servicios.get_servicio_filter(cedula=cedula_cliente, numero_serie=numero_serie)               
            if not servicio:
                return notFound()            
            return function(servicio, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@servicios_routes.route('/servicios', methods=['GET'])
def get_servicios():
    servicios = Servicios.get_servicio_all()
    return successfully(api_servicios.dump(servicios))

@servicios_routes.route('/servicio', methods=['POST'])
def post_client():
    json = request.get_json(force=True)
    servicio = Servicios.new(json)
    servicio = Help.generator_id(servicio, ID_SERVICIO)        
    if servicio.save():
        return response(api_servicio.dump(servicio))    
    return badRequest()

@servicios_routes.route('/search/servicio', methods=['POST'])
@set_servicios_by()
def get_servicio(servicio):
    print("estamos aca buscar servicio")
    return response(api_servicio.dump(servicio))

@servicios_routes.route('/servicio', methods=['PUT'])
@set_servicios_by()
def update_servicio(servicio):
    json = request.get_json(force=True)
    for key, value in json.items():
        setattr(servicio, key, value)
    if servicio.save():
        return update(api_dispositivo.dump(servicio))
    return badRequest()

@servicios_routes.route('/servicio', methods=['DELETE'])
@set_servicios_by()
def delete_servicio(servicio):
    if servicio.delete():
        return delete()
    return badRequest()

@servicios_routes.route('/servicio/cliente', methods=['POST'])
def post_servicio_cliente():
    data = request.get_json(force=True)    
    if not data:
        return badRequest(ERROR)
    # Generar id_servicio aleatorio y agregarlo al data si no existe
    Help.add_generated_id_to_data(data, ID_SERVICIO)
    if Servicios.insertar_servicio(data):
        return response(SUCCESSFUL)        
    return badEquals()
    
# microservicio para obtener el ultimo servicio insertado
@servicios_routes.route('/servicio/ultimo', methods=['GET'])
def get_ultimo_servicio():
    """
    Obtiene el último servicio insertado con información completa:
    id_servicio, email_usuario, nombre_usuario, cedula, nombre_cliente, direccion, telefono_cliente,
    marca, modelo, reporte, numero_serie, fecha_ingreso, fecha_servicio, tipo_dispositivo, tipo_servicio, pago, precio_servicio
    """
    servicio = Servicios.get_ultimo_servicio()
    if not servicio:
        return notFound()
    return successfully(api_servicio.dump(servicio))