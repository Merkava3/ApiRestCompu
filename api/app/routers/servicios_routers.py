from flask import Blueprint, request
from ..models import Servicios, db
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

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
@handle_endpoint_errors
def get_servicios():
    try:
        servicios = Servicios.get_servicio_all()
        return successfully(api_servicios.dump(servicios))
    except Exception as e:
        print(f"❌ Error obteniendo servicios: {str(e)}")
        raise

@servicios_routes.route('/servicio', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Servicio")
def post_client():
    try:
        json = request.get_json(force=True)
        if not json:
            print(f"❌ JSON vacío en POST servicio")
            return badRequest()
        servicio = Servicios.new(json)
        servicio = Help.generator_id(servicio, ID_SERVICIO)        
        if servicio.save():
            print(f"✅ Servicio creado con ID: {servicio.id_servicio}")
            return response(api_servicio.dump(servicio))    
        print(f"❌ Error al guardar servicio")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en POST servicio: {str(e)}")
        raise

@servicios_routes.route('/search/servicio', methods=['POST'])
@set_servicios_by()
def get_servicio(servicio):
    print("estamos aca buscar servicio")
    return response(api_servicio.dump(servicio))

@servicios_routes.route('/servicio', methods=['PUT'])
@set_servicios_by()
@handle_endpoint_errors
@log_operation("Actualizar Servicio")
def update_servicio(servicio):
    try:
        json = request.get_json(force=True)
        for key, value in json.items():
            setattr(servicio, key, value)
        if servicio.save():
            print(f"✅ Servicio {servicio.id_servicio} actualizado")
            return update(api_dispositivo.dump(servicio))
        print(f"❌ Error al actualizar servicio")
        return badRequest()
    except Exception as e:
        print(f"❌ Error en PUT servicio: {str(e)}")
        raise

@servicios_routes.route('/servicio', methods=['DELETE'])
@set_servicios_by()
def delete_servicio(servicio):
    if servicio.delete():
        return delete()
    return badRequest()

@servicios_routes.route('/servicio/cliente', methods=['POST'])
@handle_endpoint_errors
@log_operation("Insertar Servicio con Cliente")
def post_servicio_cliente():
    try:
        data = request.get_json(force=True)    
        if not data:
            print(f"❌ Datos vacíos en POST servicio/cliente")
            return badRequest(ERROR)
        # Generar id_servicio aleatorio y agregarlo al data si no existe
        Help.add_generated_id_to_data(data, ID_SERVICIO)
        if Servicios.insertar_servicio(data):
            print(f"✅ Servicio con cliente insertado exitosamente")
            return response(SUCCESSFULSERVICIO)        
        print(f"❌ Error al insertar servicio")
        return badEquals()
    except Exception as e:
        print(f"❌ Error en POST servicio/cliente: {str(e)}")
        raise
    
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
    try:
        data = request.get_json(force=True) or {}
        if not isinstance(data, dict):
            print(f"❌ JSON debe ser un diccionario")
            return badRequest(ERROR)

        params = data.get('params') or data.get('parametros')

        def _map_positional(pos_list):
            if len(pos_list) != len(COLUMN_LIST_ACTUALIZAR_SERVICIO):
                return None
            return {COLUMN_LIST_ACTUALIZAR_SERVICIO[i]: pos_list[i] for i in range(len(pos_list))}

        if isinstance(params, list):
            payload = _map_positional(params)
            if payload is None:
                print(f"❌ Lista de parámetros tiene longitud incorrecta. Esperado: {len(COLUMN_LIST_ACTUALIZAR_SERVICIO)}, Recibido: {len(params)}")
                return badRequest(ERROR)
        else:
            payload = data

        ok = Servicios.actualizar_servicio_completo(payload)
        if ok:
            print(f"✅ Servicio actualizado exitosamente")
            return response(SUCCESSFUL)
        print(f"❌ Error al actualizar servicio")
        return badEquals()
    except Exception as e:
        print(f"❌ Error en actualizar_servicio_completo: {str(e)}")
        raise
    