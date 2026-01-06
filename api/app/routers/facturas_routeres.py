from flask import Blueprint, request
from ..models import Facturas
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.error_handler import handle_endpoint_errors, log_operation

facturas_routes = Blueprint('facturas_routes', __name__)

def set_facturas_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_factura = json.get(ID_FACTURA)            
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if id_factura:
                factura = Facturas.get_factura(id_factura)           
            if not factura:
                return notFound()
            return function(factura, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@facturas_routes.route('/factura', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Factura")
def post_factura():
    try:
        data = request.get_json(force=True)    
        if not data:
            print(f"❌ Datos vacíos en POST factura")
            return badRequest(ERROR) 
        if Facturas.insertar_factura(data):
            print(f"✅ Factura creada exitosamente")
            return response(SUCCESSFUL)        
        print(f"❌ Error al insertar factura")
        return badEquals()
    except Exception as e:
        print(f"❌ Error en POST factura: {str(e)}")
        raise