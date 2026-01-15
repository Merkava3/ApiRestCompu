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
    return successfully(api_servicios.dump(servicios))

@servicios_routes.route('/servicio', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Servicio")
def post_client():
    json = request.get_json(force=True)
    if not json:
        return badRequest()
    servicio = Servicios.new(json)
    servicio = Help.generator_id(servicio, ID_SERVICIO)        
    if servicio.save():
        return response(api_servicio.dump(servicio))    
    return badRequest()

@servicios_routes.route('/search/servicio', methods=['POST'])
@Help.set_resource(Servicios.get_servicio_filter)
def get_servicio(servicio):
    return successfully(api_servicio.dump(servicio))

@servicios_routes.route('/servicio', methods=['PUT'])
@Help.set_resource(Servicios.get_servicio_filter)
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
@Help.set_resource(Servicios.get_servicio_filter)
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
    Obtiene el último servicio insertado con información completa:
    id_servicio, email_usuario, nombre_usuario, cedula, nombre_cliente, direccion, telefono_cliente,
    marca, modelo, reporte, numero_serie, fecha_ingreso, fecha_servicio, tipo_dispositivo, tipo_servicio, pago, precio_servicio
    """
    servicio = Servicios.get_ultimo_servicio()
    if not servicio:
        return notFound()
    return successfully(api_servicio.dump(servicio))


@servicios_routes.route('/servicio/actualizar_completo', methods=['POST'])
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

    def _map_positional(pos_list):
        if len(pos_list) != len(COLUMN_LIST_ACTUALIZAR_SERVICIO):
            return None
        return {COLUMN_LIST_ACTUALIZAR_SERVICIO[i]: pos_list[i] for i in range(len(pos_list))}

    if isinstance(params, list):
        payload = _map_positional(params)
        if payload is None:
            return badRequest(ERROR)
    else:
        payload = data

    ok = Servicios.actualizar_servicio_completo(payload)
    if ok:
        return response(SUCCESSFUL)
    return badEquals()
