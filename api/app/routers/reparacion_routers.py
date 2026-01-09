from flask import Blueprint, request
from ..models.reparaciones_model import Reparaciones
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

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
@handle_endpoint_errors
def get_reparaciones():
    reparaciones = Reparaciones.get_reparaciones_con_clientes()
    return successfully(api_reparaciones.dump(reparaciones))

@reparacion_routes.route('/reparacion', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Reparación")
def post_reparacion():
    json = request.get_json(force=True)
    if not json:
        return badRequest()
    reparacion = Reparaciones.new(json)
    reparacion = Help.generator_id(reparacion, ID_REPARACION)
    if reparacion.save():
        return response(api_reparacion.dump(reparacion))
    return badRequest()

@reparacion_routes.route('/reparacion', methods=['PUT'])
@set_reparacion_by()
@handle_endpoint_errors
@log_operation("Actualizar Reparación")
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
    return successfully(api_servicio_cliente.dump([reparacion]))

@reparacion_routes.route('/reparaciones/completas', methods=['GET'])
@handle_endpoint_errors
def get_reparaciones_completas():
    """
    Obtiene todas las reparaciones con información completa:
    id_reparacion, nombre_cliente, tipo, marca, modelo, reporte, numero_serie, estado, precio_reparacion, descripcion, fecha_entrega, fecha_ingreso
    """
    reparaciones = Reparaciones.get_reparaciones_completas()
    return successfully(api_reparaciones_completas.dump(reparaciones))

@reparacion_routes.route('/reparacion/completa', methods=['POST'])
@handle_endpoint_errors
def get_reparacion_completa():
    """
    Busca una reparación por ID o cédula del cliente con información completa:
    id_reparacion, nombre_cliente, tipo, marca, modelo, reporte, numero_serie, estado, precio_reparacion, descripcion, fecha_entrega, fecha_ingreso
    
    Body JSON puede contener:
    - id_reparacion: ID de la reparación
    - cedula: Cédula del cliente
    Se puede usar uno u otro, o ambos (buscará con OR)
    """
    json = request.get_json(force=True)
    id_reparacion = json.get(ID_REPARACION)
    cedula = json.get(CEDULA_CLIENT)
    
    # Al menos uno de los dos debe estar presente
    if not id_reparacion and not cedula:
        return badRequest()
    
    reparacion = Reparaciones.get_reparacion_completa(id_reparacion=id_reparacion, cedula=cedula)
    
    if not reparacion:
        return notFound()
    
    return successfully(api_reparacion_completa.dump(reparacion))

@reparacion_routes.route('/reparacion/insertar_completa', methods=['POST'])
@handle_endpoint_errors
@log_operation("Insertar Reparación Completa")
def post_reparacion_completa():
    """
    Inserta una reparación completa usando el procedimiento almacenado.
    Maneja cliente, dispositivo y reparación en una sola transacción.
    
    Body JSON debe contener:
    - estado: Estado de la reparación (requerido)
    - precio_reparacion: Precio de la reparación (requerido)
    - descripcion: Descripción de la reparación (requerido)
    - cedula: Cédula del cliente (requerido)
    - numero_serie o dispositivo_id_reparacion: ID del dispositivo (uno requerido)
    
    Campos opcionales: tipo, marca, modelo, reporte, fecha_ingreso, 
                      nombre_cliente, direccion, telefono_cliente
    
    Nota: id_reparacion se genera automáticamente. fecha_entrega no es requerida.
    """
    try:
        import json
        import re
        
        # Obtener JSON crudamente
        raw_data = request.get_data(as_text=True)
        
        # Sanitizar: reemplazar newlines dentro de strings con espacios
        # Esto es más agresivo pero maneja JSON con newlines literales en strings
        sanitized_raw = re.sub(
            r'(?<!\\)(?:\\\\)*[\n\r](?=[^"]*")',  # newlines antes de comillas
            ' ',
            raw_data
        )
        
        # Remover caracteres de control que no sean espacios o tabulaciones
        sanitized_raw = ''.join(
            char if (ord(char) >= 32 or char == '\t') else ''
            for char in sanitized_raw
        )
        
        # Parsear el JSON sanitizado
        data = json.loads(sanitized_raw) if sanitized_raw else {}
    except (ValueError, json.JSONDecodeError) as e:
        return badRequest(f"JSON inválido: {str(e)}")
    
    # Validar estructura de datos
    if not isinstance(data, dict):
        return badRequest(ERROR)
    
    # Validar campos requeridos usando patrón Strategy
    is_valid, missing = Help.validate_required_fields(
        data, 
        ['estado', 'precio_reparacion', 'descripcion', 'cedula']
    )
    if not is_valid:
        msg = f"Campos requeridos faltantes: {', '.join(missing)}"
        return badRequest(msg)
    
    # Validar que tenga al menos uno: numero_serie o dispositivo_id_reparacion
    if not Help.validate_at_least_one_field(data, ['numero_serie', 'dispositivo_id_reparacion']):
        return badRequest("Debe proporcionarse numero_serie o dispositivo_id_reparacion")
    
    # Generar ID automáticamente (nunca debe venir en el JSON)
    Help.add_generated_id_to_data(data, ID_REPARACION)
    
    # Ejecutar operación
    success = Reparaciones.insertar_reparacion_completa(data)
    if success:
        return response(SUCCESSFULREPARACION)
    
    return badRequest("Error al insertar reparación completa")
    