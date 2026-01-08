"""
Manejador centralizado de errores y logging para todos los endpoints.
Proporciona decoradores y utilidades para manejo consistente de excepciones.
"""
import logging
from functools import wraps
from flask import jsonify
import traceback

# Importar excepciones de SQLAlchemy y psycopg2
from sqlalchemy.exc import SQLAlchemyError, OperationalError
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

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


class DatabaseException(APIException):
    """Excepción para errores de base de datos"""
    def __init__(self, message="Error en la base de datos", original_error=None, status_code=500):
        self.original_error = original_error
        super().__init__(message, status_code, {"database_error": True})


def _handle_database_error(error):
    """
    Analiza y formatea errores de base de datos.
    Retorna tuple: (mensaje_usuario, detalles_log)
    """
    error_msg = str(error)
    error_type = type(error).__name__
    
    # Manejo específico de errores de conexión
    if "SSL connection has been closed" in error_msg or "OperationalError" in error_type:
        return (
            "Error de conexión con la base de datos. Por favor, intente nuevamente.",
            {"error_type": "CONNECTION_ERROR", "details": "SSL connection closed unexpectedly"}
        )
    
    # Manejo de errores de integridad de datos
    if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
        return (
            "El registro ya existe o viola una restricción de unicidad.",
            {"error_type": "INTEGRITY_ERROR", "details": error_msg}
        )
    
    # Manejo de errores genéricos de base de datos
    if HAS_PSYCOPG2 and isinstance(error, (psycopg2.DatabaseError, psycopg2.OperationalError)):
        return (
            "Error al procesar la solicitud en la base de datos.",
            {"error_type": "DATABASE_ERROR", "details": error_msg}
        )
    
    if isinstance(error, (OperationalError, SQLAlchemyError)):
        return (
            "Error al acceder a la base de datos.",
            {"error_type": "DATABASE_ERROR", "details": error_msg}
        )
    
    # Error genérico
    return (
        "Error al procesar la solicitud.",
        {"error_type": "UNKNOWN", "details": error_msg}
    )


def handle_endpoint_errors(func):
    """
    Decorador para capturar y loguear errores en endpoints.
    Maneja errores de base de datos, excepciones API y errores inesperados.
    
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
            # Errores controlados de API
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
            
        except (SQLAlchemyError, Exception) as e:
            # Manejo de errores de base de datos y excepciones genéricas
            error_type = type(e).__name__
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            
            # Determinar si es error de base de datos
            is_db_error = isinstance(e, (SQLAlchemyError, OperationalError)) or \
                         (HAS_PSYCOPG2 and isinstance(e, (psycopg2.DatabaseError, psycopg2.OperationalError))) or \
                         "SSL connection" in error_msg or "OperationalError" in error_type
            
            if is_db_error:
                # Manejo especializado de errores de BD
                user_msg, db_details = _handle_database_error(e)
                logger.error(f"Error de Base de Datos en {func.__name__}: {error_type} - {error_msg}")
                print(f"\n⚠️  ERROR DE BASE DE DATOS en '{func.__name__}':")
                print(f"   Tipo: {error_type}")
                print(f"   Mensaje: {error_msg}\n")
                
                return jsonify({
                    "code": 503,
                    "success": False,
                    "message": user_msg,
                    "error_type": "DATABASE_ERROR",
                    "details": db_details
                }), 503
            else:
                # Errores generales inesperados
                logger.error(f"Error inesperado en {func.__name__}: {error_type} - {error_msg}")
                print(f"\n🔴 ERROR NO CONTROLADO en endpoint '{func.__name__}':")
                print(f"   Tipo: {error_type}")
                print(f"   Mensaje: {error_msg}")
                print(f"\n   Stack Trace:")
                print(f"   {stack_trace}\n")
                
                return jsonify({
                    "code": 500,
                    "success": False,
                    "message": "Error interno del servidor",
                    "error_type": error_type,
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
