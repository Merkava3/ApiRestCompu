from flask import Blueprint, request
from ..models import Servicios, db
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation
from ..cache import with_cache, invalidate_cache
from ..models.auth_decorator import token_required, role_required

servicios_routes = Blueprint('servicios_routes', __name__)

@servicios_routes.route('/servicios', methods=['GET'])
@handle_endpoint_errors
@with_cache(resource='servicios', operation='get_all')
def get_all():
    """Listar todos los servicios."""
    res = Servicios.get_servicio_all()
    return successfully(api_servicios_completos.dump(res))

@servicios_routes.route('/servicio', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Servicio")
@invalidate_cache(resource='servicios')
def create():
    """Crear nuevo servicio."""
    data = request.get_json(force=True)
    if not data: return badRequest()
    Help.add_generated_id_to_data(data, ID_SERVICIO)
    if Servicios.insertar_servicio(data):
        return response(SUCCESSFULSERVICIO)
    return badRequest()

@servicios_routes.route('/search/servicio', methods=['POST'])
@Help.set_resource(Servicios.get_servicio_filter, many=True)
def search(servicios):
    """Buscar servicios por filtro."""
    return successfully(api_servicios_completos.dump(servicios))

@servicios_routes.route('/servicio', methods=['PUT'])
@Help.set_resource(Servicios.get_servicio_orm)
@handle_endpoint_errors
@log_operation("Actualizar Parcial")
@invalidate_cache(resource='servicios')
def update_partial(servicio):
    """Actualización parcial de estado/fecha."""
    json = request.get_json(force=True)
    if 'estado' in json: 
        if Help.validate_status(json['estado'], ESTADOS_SERVICIO):
            servicio.estado_servicio = json['estado']
        else: return badRequest("Estado inválido")
    if 'fecha_entrega' in json: servicio.fecha_entrega = json['fecha_entrega']
    return successfully(api_servicio_update.dump(servicio), "Actualizado") if servicio.save() else badRequest()

@servicios_routes.route('/servicio/estado', methods=['PUT'])
@handle_endpoint_errors
@token_required
@role_required('tecnico')
@log_operation("Estado Tarea")
@invalidate_cache(resource='servicios')
def update_task_status():
    """Actualizar estado específico (ej: en_proceso)."""
    data = request.get_json(force=True)
    id_serv = data.get(ID_SERVICIO)
    estado = data.get('estado_servicio')
    descripcion = data.get('descripcion')
    
    if id_serv and estado and descripcion and Servicios.actualizar_estado(id_serv, estado, descripcion):
        return successfully(message="Estado actualizado")
    return badRequest("ID, Estado o Descripción no válido")

@servicios_routes.route('/servicio', methods=['DELETE'])
@Help.set_resource(Servicios.get_servicio_orm)
@invalidate_cache(resource='servicios')
def delete(servicio):
    """Eliminar servicio."""
    return successfully(message="Eliminado") if servicio.delete() else badRequest()

@servicios_routes.route('/servicio/cliente', methods=['POST'])
@handle_endpoint_errors
@log_operation("Insertar con Cliente")
def create_with_client():
    """Insertar servicio junto con datos de cliente."""
    data = request.get_json(force=True)
    if not data: return badRequest(ERROR)
    Help.add_generated_id_to_data(data, ID_SERVICIO)
    Help.add_default_value_to_data(data, 'estado_servicio', 'recibido')
    if Servicios.insertar_servicio(data):
        return response(SUCCESSFULSERVICIO)
    return badEquals()

@servicios_routes.route('/servicio/ultimo', methods=['GET'])
@handle_endpoint_errors
@with_cache(resource='servicios', operation='get_ultimo')
def get_last_10():
    """Obtener últimos 10 servicios."""
    res = Servicios.get_ultimo_servicio()
    return successfully(api_servicios_completos.dump(res)) if res else notFound()

@servicios_routes.route('/servicio/update', methods=['POST'])
@handle_endpoint_errors
@log_operation("Actualizar Completo")
@invalidate_cache(resource='servicios')
def update_full():
    """Actualización completa vía SP."""
    data = request.get_json(force=True) or {}
    params = data.get('params') or data.get('parametros')
    if isinstance(params, list):
        if len(params) != len(COLUMN_LIST_ACTUALIZAR_SERVICIO):
            return badRequest("Parámetros insuficientes")
        payload = {COLUMN_LIST_ACTUALIZAR_SERVICIO[i]: params[i] for i in range(len(params))}
    else:
        payload = data

    if Servicios.actualizar_servicio_completo(payload):
        return response(SUCCESSFULSERVICIO)
    return badEquals()

@servicios_routes.route('/servicio/entrega_fecha', methods=['PUT'])
@handle_endpoint_errors
@log_operation("Fecha Entrega")
@invalidate_cache(resource='servicios')
def update_delivery_date():
    """Actualizar fecha de entrega a NOW()."""
    data = request.get_json(force=True)
    if data and Servicios.actualizar_fecha_entrega(data):
        return successfully({"mensaje": "Fecha actualizada"}, "Éxito")
    return badRequest(ERROR_NO_ENCONTRADO)

@servicios_routes.route('/search/servicio/cedula', methods=['POST'])
@handle_endpoint_errors
def get_by_cedula():
    """Buscar último servicio por cédula."""
    data = request.get_json(force=True)
    if not data or 'cedula' not in data: return badRequest(ERROR)
    res = Servicios.get_servicio_by_cedula(data['cedula'])
    return successfully(api_servicio_cedula.dump(res)) if res else notFound(ERROR_NO_ENCONTRADO)

@servicios_routes.route('/servicio/ultimo_detalle', methods=['GET'])
@handle_endpoint_errors
@with_cache(resource='servicios', operation='get_ultimo_detalle')
def get_last_detail():
    """Detalle del servicio más reciente."""
    res = Servicios.get_ultimo_servicio_detalle()
    return successfully(api_servicio_ultimo_detalle.dump(res)) if res else notFound(ERROR_NO_ENCONTRADO)

@servicios_routes.route('/servicio/reporte', methods=['GET'])
@handle_endpoint_errors
@with_cache(resource='servicios', operation='get_reporte')
def get_report():
    """Generar reporte general."""
    res = Servicios.get_servicio_reporte()
    return successfully(api_servicios_reporte.dump(res)) if res else notFound(ERROR_NO_ENCONTRADO)

@servicios_routes.route('/servicio/tareas', methods=['GET'])
@handle_endpoint_errors
@token_required
@role_required('tecnico')
@with_cache(resource='servicios', operation='get_tareas')
def get_tasks():
    """Listar servicios en estados activos (tareas)."""
    res = Servicios.get_servicios_tareas()
    return successfully(api_servicios_tareas.dump(res)) if res else notFound(ERROR_NO_ENCONTRADO)

@servicios_routes.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud del servidor."""
    return jsonify({"status": "ok", "message": "Servidor funcionando correctamente"}), 200
