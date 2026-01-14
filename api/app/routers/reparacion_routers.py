import json
import re
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
                reparaciones = Reparaciones.get_reparaciones_filter(cedula=cedula_cliente, numero_serie=numero_serie)
                reparacion = reparaciones[0] if reparaciones else None
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

@reparacion_routes.route('/consulta/reparacion', methods=['POST'])
@handle_endpoint_errors
def get_reparacion_cliente():
    """
    Busca reparaciones por ID o cédula del cliente.
    Retorna los datos detallados ordenados por fecha de ingreso (más reciente primero).
    """
    json_data = request.get_json(force=True)
    id_reparacion = json_data.get(ID_REPARACION)
    cedula_cliente = json_data.get(CEDULA_CLIENT)
    
    if not id_reparacion and not cedula_cliente:
        return badRequest("Debe proporcionar ID de reparación o cédula del cliente")
    
    reparaciones = Reparaciones.get_reparaciones_filter(
        cedula=cedula_cliente, 
        id_reparacion=id_reparacion
    )
    
    if not reparaciones:
        return notFound("No se encontraron reparaciones")
        
    return successfully(api_reparaciones.dump(reparaciones))


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
    data = request.get_json(force=True)
    
    # Generar ID (Obligatorio para el SP)
    Help.add_generated_id_to_data(data, ID_REPARACION)
    
    # Ejecutar operación
    id_reparacion = Reparaciones.insertar_reparacion_completa(data)
    
    if id_reparacion:
        # Retornar la reparación completa (con fechas y datos generados por BD)
        reparacion = Reparaciones.get_reparacion_completa(id_reparacion=id_reparacion)
        return successfully(api_reparacion_completa.dump(reparacion))
    
    return badRequest("Error al insertar reparación completa")
