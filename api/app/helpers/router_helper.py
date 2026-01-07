"""
Helper para routers que proporciona decoradores y funciones comunes.
Reduce duplicación de código en los endpoints.
"""
from functools import wraps
from flask import request, jsonify
from typing import Callable, Optional, Any, Dict
import logging

from .error_handler import APIException
from .response import ResponseHelper

logger = logging.getLogger(__name__)


def get_json_or_400():
    """
    Obtiene el JSON del request o lanza una excepción 400.
    
    Returns:
        dict: Datos JSON del request
        
    Raises:
        APIException: Si el JSON no es válido o está vacío
    """
    data = request.get_json(force=True) or {}
    if not isinstance(data, dict):
        raise APIException("El payload debe ser un objeto JSON válido", status_code=400)
    return data


def find_model_by_field(model_class, field_name: str, field_value: Any, 
                        not_found_message: str = "Recurso no encontrado"):
    """
    Busca un modelo por un campo específico.
    
    Args:
        model_class: Clase del modelo SQLAlchemy
        field_name: Nombre del campo a buscar
        field_value: Valor a buscar
        not_found_message: Mensaje si no se encuentra
    
    Returns:
        Instancia del modelo encontrado
    
    Raises:
        APIException: Si no se encuentra el modelo
    """
    model = model_class.query.filter_by(**{field_name: field_value}).first()
    if not model:
        raise APIException(not_found_message, status_code=404)
    return model


def set_model_by_field(field_name: str, model_class, get_method: Optional[Callable] = None):
    """
    Decorador genérico para obtener un modelo por un campo específico del JSON.
    
    Args:
        field_name: Nombre del campo en el JSON
        model_class: Clase del modelo
        get_method: Método estático opcional para obtener el modelo (ej: Cliente.get_cliente)
    
    Uso:
        @router.route('/endpoint', methods=['PUT'])
        @set_model_by_field('id_cliente', Cliente, Cliente.get_id_client)
        def update_client(cliente):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = get_json_or_400()
                field_value = data.get(field_name)
                
                if field_value is None:
                    raise APIException(f"Campo '{field_name}' requerido", status_code=400)
                
                # Usar método personalizado si se proporciona, sino usar query genérico
                if get_method:
                    model = get_method(field_value)
                else:
                    model = model_class.query.filter_by(**{field_name: field_value}).first()
                
                if not model:
                    raise APIException("Recurso no encontrado", status_code=404)
                
                return func(model, *args, **kwargs)
            except APIException:
                raise
            except Exception as e:
                logger.error(f"Error en decorador set_model_by_field: {e}", exc_info=True)
                raise APIException("Error procesando la solicitud", status_code=500)
        return wrapper
    return decorator


def validate_json_fields(required_fields: Optional[list] = None, 
                         optional_fields: Optional[list] = None):
    """
    Decorador para validar campos JSON en el request.
    
    Args:
        required_fields: Lista de campos requeridos
        optional_fields: Lista de campos opcionales permitidos
    
    Uso:
        @router.route('/endpoint', methods=['POST'])
        @validate_json_fields(required_fields=['nombre', 'email'])
        def create_resource():
            data = request.get_json()
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = get_json_or_400()
                
                if required_fields:
                    missing = [f for f in required_fields if f not in data or data[f] is None]
                    if missing:
                        raise APIException(
                            f"Campos requeridos faltantes: {', '.join(missing)}",
                            status_code=400,
                            details={"missing_fields": missing}
                        )
                
                # Validar que no haya campos no permitidos (si se especificaron opcionales)
                if required_fields and optional_fields:
                    allowed = set(required_fields + optional_fields)
                    provided = set(data.keys())
                    invalid = provided - allowed
                    if invalid:
                        raise APIException(
                            f"Campos no permitidos: {', '.join(invalid)}",
                            status_code=400,
                            details={"invalid_fields": list(invalid)}
                        )
                
                return func(*args, **kwargs)
            except APIException:
                raise
            except Exception as e:
                logger.error(f"Error en validación JSON: {e}", exc_info=True)
                raise APIException("Error validando datos", status_code=400)
        return wrapper
    return decorator


def handle_crud_operations(model_class, schema, 
                          id_field: str = 'id',
                          get_method: Optional[Callable] = None,
                          name: str = "Recurso"):
    """
    Crea handlers genéricos para operaciones CRUD.
    
    Args:
        model_class: Clase del modelo SQLAlchemy
        schema: Schema de Marshmallow para serialización
        id_field: Nombre del campo ID
        get_method: Método estático opcional para obtener por ID
        name: Nombre del recurso para mensajes
    
    Returns:
        Dict con funciones handler para CRUD
    """
    
    def get_all():
        """Obtiene todos los recursos."""
        try:
            items = model_class.query.all()
            return ResponseHelper.success(schema.dump(items, many=True))
        except Exception as e:
            logger.error(f"Error obteniendo {name}: {e}", exc_info=True)
            raise APIException(f"Error obteniendo {name}", status_code=500)
    
    def get_one(model):
        """Obtiene un recurso específico."""
        return ResponseHelper.success(schema.dump(model))
    
    def create():
        """Crea un nuevo recurso."""
        try:
            data = get_json_or_400()
            instance = model_class.create_from_dict(data)
            
            if instance.save():
                logger.info(f"{name} creado: {instance}")
                return ResponseHelper.created(schema.dump(instance))
            
            raise APIException(f"Error al crear {name}", status_code=500)
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error creando {name}: {e}", exc_info=True)
            raise APIException(f"Error al crear {name}", status_code=500)
    
    def update(model):
        """Actualiza un recurso existente."""
        try:
            data = get_json_or_400()
            model.update_from_dict(data, exclude=[id_field])
            
            if model.save():
                logger.info(f"{name} actualizado: {model}")
                return ResponseHelper.success(schema.dump(model), "Registro actualizado")
            
            raise APIException(f"Error al actualizar {name}", status_code=500)
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error actualizando {name}: {e}", exc_info=True)
            raise APIException(f"Error al actualizar {name}", status_code=500)
    
    def delete(model):
        """Elimina un recurso."""
        try:
            if model.delete():
                logger.info(f"{name} eliminado: {model}")
                return ResponseHelper.success(None, "Registro eliminado")
            
            raise APIException(f"Error al eliminar {name}", status_code=500)
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error eliminando {name}: {e}", exc_info=True)
            raise APIException(f"Error al eliminar {name}", status_code=500)
    
    return {
        'get_all': get_all,
        'get_one': get_one,
        'create': create,
        'update': update,
        'delete': delete
    }
