"""Helper para routers con utilidades comunes."""
from functools import wraps
from flask import request
from .error_handler import APIException
from .response import ResponseHelper

def get_json():
    """Obtiene JSON o lanza error 400."""
    data = request.get_json(force=True) or {}
    if not isinstance(data, dict):
        raise APIException("Payload JSON inválido", 400)
    return data

def set_model(field, model_class, get_method=None):
    """Decorador para inyectar recurso desde un campo JSON."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            val = get_json().get(field)
            if val is None: raise APIException(f"Campo '{field}' requerido", 400)
            model = get_method(val) if get_method else model_class.query.filter_by(**{field: val}).first()
            if not model: raise APIException("Recurso no encontrado", 404)
            return f(model, *args, **kwargs)
        return wrapper
    return decorator

def validate_fields(required=None, allowed=None):
    """Valida campos obligatorios y/o permitidos."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data, req = get_json(), required or []
            missing = [p for p in req if p not in data or data[p] is None]
            if missing: raise APIException(f"Faltan: {', '.join(missing)}", 400)
            if allowed:
                invalid = [p for p in data if p not in set(req + allowed)]
                if invalid: raise APIException(f"No permitidos: {', '.join(invalid)}", 400)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def crud_factory(model, schema, name="Recurso"):
    """Genera handlers CRUD estándar para un modelo."""
    def create():
        item = model.create_from_dict(get_json())
        return ResponseHelper.created(schema.dump(item)) if item.save() else ResponseHelper.error(f"Error al crear {name}")

    def update(item):
        item.update_from_dict(get_json())
        return ResponseHelper.success(schema.dump(item), "Actualizado") if item.save() else ResponseHelper.error(f"Error al actualizar {name}")

    return {
        'get_all': lambda: ResponseHelper.success(schema.dump(model.query.all(), many=True)),
        'get_one': lambda item: ResponseHelper.success(schema.dump(item)),
        'create': create,
        'update': update,
        'delete': lambda item: ResponseHelper.success(None, "Eliminado") if item.delete() else ResponseHelper.error(f"Error al eliminar {name}")
    }
