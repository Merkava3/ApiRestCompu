"""
Manejador centralizado de errores y logging para todos los endpoints.
Proporciona decoradores y utilidades para manejo consistente de excepciones.
"""
import logging
from functools import wraps
from flask import jsonify
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIException(Exception):
    """Excepción base para errores de API"""
    def __init__(self, message, status_code=400, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


def handle_endpoint_errors(func):
    """
    Decorador para capturar y loguear errores en endpoints.
    Imprime automáticamente cualquier excepción en la consola y responde con detalles.
    
    Uso:
        @handle_endpoint_errors
        def mi_endpoint():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIException as e:
            logger.error(f"API Error en {func.__name__}: {e.message}", extra={"details": e.details})
            print(f"\n❌ ERROR en endpoint '{func.__name__}':")
            print(f"   Mensaje: {e.message}")
            if e.details:
                print(f"   Detalles: {e.details}")
            print(f"   Código HTTP: {e.status_code}\n")
            return jsonify({
                "code": e.status_code,
                "success": False,
                "message": e.message,
                "details": e.details
            }), e.status_code
        except Exception as e:
            # Capturar cualquier excepción no esperada
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            
            logger.error(f"Error inesperado en {func.__name__}: {error_msg}")
            print(f"\n🔴 ERROR NO CONTROLADO en endpoint '{func.__name__}':")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {error_msg}")
            print(f"\n   Stack Trace:")
            print(f"   {stack_trace}\n")
            
            return jsonify({
                "code": 500,
                "success": False,
                "message": "Error interno del servidor",
                "error_type": type(e).__name__,
                "details": error_msg
            }), 500
    return wrapper


def log_operation(operation_name):
    """
    Decorador para loguear operaciones importantes en endpoints.
    
    Uso:
        @log_operation("Crear cliente")
        def post_client():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                print(f"\n📌 Iniciando operación: {operation_name}")
                result = func(*args, **kwargs)
                print(f"✅ Operación '{operation_name}' completada exitosamente\n")
                return result
            except Exception as e:
                print(f"❌ Operación '{operation_name}' falló: {str(e)}\n")
                raise
        return wrapper
    return decorator


def safe_model_call(model_method, *args, **kwargs):
    """
    Ejecuta un método del modelo con manejo de errores mejorado.
    
    Uso:
        result = safe_model_call(Cliente.get_cliente, cedula)
    
    Retorna:
        tuple: (success, data, error_message)
    """
    try:
        result = model_method(*args, **kwargs)
        return True, result, None
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error en llamada a modelo {model_method.__name__}: {error_msg}")
        print(f"⚠️  Error en modelo: {error_msg}")
        return False, None, error_msg


def validate_json_payload(required_fields=None):
    """
    Decorador para validar que el payload JSON tenga los campos requeridos.
    
    Uso:
        @validate_json_payload(required_fields=['cedula', 'nombre'])
        def post_client():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request
            try:
                data = request.get_json(force=True) or {}
                if required_fields:
                    missing = [f for f in required_fields if f not in data or not data[f]]
                    if missing:
                        raise APIException(
                            f"Campos requeridos faltantes: {', '.join(missing)}",
                            status_code=400,
                            details={"missing_fields": missing}
                        )
                return func(*args, **kwargs)
            except APIException:
                raise
            except Exception as e:
                raise APIException(
                    "Error procesando JSON",
                    status_code=400,
                    details={"error": str(e)}
                )
        return wrapper
    return decorator
