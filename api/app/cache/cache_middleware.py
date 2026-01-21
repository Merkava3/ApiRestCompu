"""
Middleware de caché para integración transparente con Flask.
Maneja invalidación automática de caché en operaciones de modificación.
"""
from flask import request, g
from functools import wraps
from typing import Callable, Optional
from .cache_manager import CacheManager
from .cache_config import CACHE_ENABLED, CACHE_INVALIDATE_ON, get_ttl


class CacheMiddleware:
    """
    Middleware para manejar caché automáticamente en endpoints.
    Implementa Single Responsibility: solo gestiona caché HTTP.
    """
    
    def __init__(self):
        self.cache_mgr = CacheManager()
    
    def should_cache_request(self) -> bool:
        """Determina si la petición debe ser cacheada."""
        return (
            CACHE_ENABLED and
            request.method == 'GET' and
            not request.args.get('no_cache')
        )
    
    def should_invalidate_cache(self) -> bool:
        """Determina si debe invalidar caché después de la petición."""
        return CACHE_ENABLED and request.method in CACHE_INVALIDATE_ON
    
    def get_cache_key_from_request(self) -> str:
        """Genera clave de caché basada en la petición HTTP."""
        # Usar el endpoint y parámetros como clave
        endpoint = request.endpoint or 'unknown'
        params = dict(request.args)
        params.update(request.form.to_dict() if request.form else {})
        
        return self.cache_mgr.generate_key(
            namespace=endpoint.split('.')[0] if '.' in endpoint else 'api',
            identifier=endpoint,
            params=params if params else None
        )
    
    def init_app(self, app):
        """Registra el middleware con la aplicación Flask."""
        @app.before_request
        def before_request_cache():
            """Ejecuta antes de cada petición."""
            g.cache_key = self.get_cache_key_from_request() if self.should_cache_request() else None
        
        @app.after_request
        def after_request_cache(response):
            """Ejecuta después de cada petición."""
            # Invalidar caché si es operación de modificación
            if self.should_invalidate_cache():
                self.cache_mgr.clear()
            
            return response


def with_cache(
    resource: str,
    operation: str,
    key_params: Optional[list] = None
) -> Callable:
    """
    Decorador mejorado para cachear respuestas de endpoints.
    
    Args:
        resource: Tipo de recurso
        operation: Tipo de operación
        key_params: Parámetros para generar clave única
    
    Ejemplo:
        @with_cache(resource='servicios', operation='get_all')
        def get_servicios():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHE_ENABLED:
                return func(*args, **kwargs)
            
            cache_mgr = CacheManager()
            ttl = get_ttl(resource, operation)
            
            # Construir parámetros para clave
            params = {}
            if key_params:
                for param in key_params:
                    if param in kwargs:
                        params[param] = kwargs[param]
            
            # Generar clave
            cache_key = cache_mgr.generate_key(resource, operation, params or None)
            
            # Intentar obtener del caché
            cached_result = cache_mgr.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear
            result = func(*args, **kwargs)
            cache_mgr.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(resource: str) -> Callable:
    """
    Decorador para invalidar caché de un recurso específico.
    Se ejecuta después de la función.
    
    Args:
        resource: Tipo de recurso a invalidar
    
    Ejemplo:
        @invalidate_cache(resource='servicios')
        def crear_servicio(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if CACHE_ENABLED:
                CacheManager().clear()  # Para una solución robusta, invalidar solo el recurso
            
            return result
        
        return wrapper
    return decorator
