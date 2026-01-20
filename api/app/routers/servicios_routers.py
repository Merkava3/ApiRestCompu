from flask import Blueprint, request
from ..models import Servicios, db
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

servicios_routes = Blueprint('servicios_routes', __name__)

@servicios_routes.route('/servicios', methods=['GET'])
@handle_endpoint_errors
def get_servicios():
    servicios = Servicios.get_servicio_all()
    return successfully(api_servicios_completos.dump(servicios))

@servicios_routes.route('/servicio', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Servicio")
def post_client():
    json_data = request.get_json(force=True)
    if not json_data:
        return badRequest()
    
    # Generar ID y asignarlo al JSON
    Help.add_generated_id_to_data(json_data, ID_SERVICIO)
    
    if Servicios.insertar_servicio(json_data):
        return response(SUCCESSFULSERVICIO)    
    return badRequest()

@servicios_routes.route('/search/servicio', methods=['POST'])
@Help.set_resource(Servicios.get_servicio_filter, many=True)
def get_servicio(servicios):
    return successfully(api_servicios_completos.dump(servicios))

@servicios_routes.route('/servicio', methods=['PUT'])
@Help.set_resource(Servicios.get_servicio_orm)
@handle_endpoint_errors
@log_operation("Actualizar Servicio")
def update_servicio(servicio):
    json = request.get_json(force=True)
    # Se aplican actualizaciones específicamente para estado y fecha_servicio
    if 'estado' in json:
        servicio.estado = json['estado']
    if 'fecha_servicio' in json:
        servicio.fecha_servicio = json['fecha_servicio']

    if servicio.save():
        return successfully(api_servicio_update.dump(servicio), "Registro Actualizado")
    return badRequest()

@servicios_routes.route('/servicio', methods=['DELETE'])
@Help.set_resource(Servicios.get_servicio_orm)
def delete_servicio(servicio):
    if servicio.delete():
        return successfully(message="Registro eliminado")
    return badRequest()

@servicios_routes.route('/servicio/cliente', methods=['POST'])
@handle_endpoint_errors
@log_operation("Insertar Servicio con Cliente")
def post_servicio_cliente():
    data = request.get_json(force=True)    
    if not data:
        return badRequest(ERROR)
    # Generar id_servicio aleatorio y agregarlo al data si no existe
    Help.add_generated_id_to_data(data, ID_SERVICIO)
    if Servicios.insertar_servicio(data):
        return response(SUCCESSFULSERVICIO)        
    return badEquals()
    
# microservicio para obtener el ultimo servicio insertado
@servicios_routes.route('/servicio/ultimo', methods=['GET'])
def get_ultimo_servicio():
    """
    Obtiene los últimos 10 servicios insertados con información completa.
    """
    servicios = Servicios.get_ultimo_servicio()
    if not servicios:
        return notFound()
    return successfully(api_servicios_completos.dump(servicios))

@servicios_routes.route('/servicio/update', methods=['POST'])
@handle_endpoint_errors
@log_operation("Actualizar Servicio Completo")
def actualizar_servicio_completo():
    """Recibe JSON y actualiza un servicio completo.

    Se acepta either:
    - Un diccionario con las claves esperadas por el procedimiento, o
    - Un array posicional en `params`/`parametros` en el mismo orden que
      `COLUMN_LIST_ACTUALIZAR_SERVICIO`.
    """
    data = request.get_json(force=True) or {}
    if not isinstance(data, dict):
        return badRequest(ERROR)

    params = data.get('params') or data.get('parametros')

    if isinstance(params, list):
        if len(params) != len(COLUMN_LIST_ACTUALIZAR_SERVICIO):
            return badRequest("Número de parámetros incorrecto")
            
        payload = {COLUMN_LIST_ACTUALIZAR_SERVICIO[i]: params[i] for i in range(len(params))}
    else:
        payload = data

    ok = Servicios.actualizar_servicio_completo(payload)
    if ok:
        return response(SUCCESSFULSERVICIO)
    return badEquals()

@servicios_routes.route('/servicio/entrega_fecha', methods=['PUT'])
@handle_endpoint_errors
@log_operation("Actualizar Fecha Entrega")
def actualizar_fecha_entrega():
    """
    Actualiza solo la fecha de entrega de un servicio específico a NOW().
    Requiere id_servicio en el body.
    """
    json_data = request.get_json(force=True)
    if not json_data:
        return badRequest(ERROR)
        
    if Servicios.actualizar_fecha_entrega(json_data):
        return successfully({"mensaje": "Fecha de entrega actualizada correctamente"}, "Actualización Exitosa")
    
    return badRequest(ERROR_NO_ENCONTRADO)


@servicios_routes.route('/search/servicio/cedula', methods=['POST'])
@handle_endpoint_errors
def get_servicio_por_cedula():
    """
    Obtiene el último servicio asociado a una cédula.
    """
    data = request.get_json(force=True)
    if not data or 'cedula' not in data:
        return badRequest(ERROR)
    
    servicio = Servicios.get_servicio_by_cedula(data['cedula'])
    if servicio:
        return successfully(api_servicio_cedula.dump(servicio))
    return notFound(ERROR_NO_ENCONTRADO)
