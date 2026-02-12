"""Manejador centralizado de errores y logging."""
import logging
import traceback
from functools import wraps
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Configuración básica de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIException(Exception):
    """Error base para la API."""
    def __init__(self, message, status_code=400, details=None):
        self.message, self.status_code, self.details = message, status_code, details or {}
        super().__init__(message)

def _handle_db_error(e):
    """Analiza y traduce errores de DB a mensajes legibles."""
    msg = str(e).lower()
    if "ssl connection" in msg or "operationalerror" in type(e).__name__.lower():
        return "Error de conexión con la base de datos.", {"type": "CONNECTION"}
    if "duplicate key" in msg or "unique constraint" in msg:
        return "El registro ya existe.", {"type": "INTEGRITY"}
    return "Error al procesar la solicitud en la base de datos.", {"type": "DATABASE"}

def handle_endpoint_errors(func):
    """Decorador global para captura de errores en endpoints."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIException as e:
            logger.error(f"API Error: {e.message}")
            return jsonify({"code": e.status_code, "success": False, "message": e.message, "details": e.details}), e.status_code
        except Exception as e:
            # Manejo de bloqueos de recursos (Concurrency)
            if "cannot notify on un-acquired lock" in str(e):
                return jsonify({"code": 503, "success": False, "message": "Servidor ocupado, reintente.", "details": "resource_lock"}), 503
            
            # Clasificación de error (DB vs General)
            if isinstance(e, (SQLAlchemyError, OperationalError)) or "ssl connection" in str(e).lower():
                from ..models import db
                db.session.rollback()  # Asegurar liberación ante errores de conexión
                user_msg, details = _handle_db_error(e)
                logger.error(f"DB Error: {str(e)}")
                # Si es error de conexión, el usuario suele recargar. 503 indica que es temporal.
                return jsonify({"code": 503, "success": False, "message": user_msg, "details": details}), 503
            
            logger.error(f"Unexpected Error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"code": 500, "success": False, "message": "Error interno", "details": str(e)}), 500
    return wrapper

def log_operation(name):
    """Loguea el inicio y fin de una operación."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(f"📌 Iniciando: {name}")
            res = f(*args, **kwargs)
            print(f"✅ Completado: {name}")
            return res
        return wrapper
    return decorator

def validate_json_payload(required=None):
    """Valida presencia de campos en el JSON."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from flask import request
            data = request.get_json(force=True) or {}
            missing = [f for f in (required or []) if f not in data or not data[f]]
            if missing:
                raise APIException(f"Faltan campos: {', '.join(missing)}", 400, {"missing": missing})
            return f(*args, **kwargs)
        return wrapper
    return decorator
