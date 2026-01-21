"""
Gestor de caché centralizado con soporte para múltiples estrategias.
Implementa SOLID Principles: Single Responsibility, Open/Closed, Dependency Inversion.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Dict
from functools import wraps
import hashlib
import json
from datetime import datetime, timedelta
import threading


class CacheStrategy(ABC):
    """Interfaz abstracta para estrategias de caché (Dependency Inversion)."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena un valor en el caché."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Elimina un valor del caché."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Limpia todo el caché."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Verifica si una clave existe."""
        pass


class InMemoryCache(CacheStrategy):
    """
    Implementación de caché en memoria con expiración TTL.
    Thread-safe para entornos multi-threading.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Inicializa el caché en memoria.
        
        Args:
            max_size: Número máximo de entradas permitidas.
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor con validación de expiración."""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Verificar expiración
            if entry['expires_at'] and datetime.now() > entry['expires_at']:
                del self.cache[key]
                return None
            
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena valor con control de límite de memoria."""
        with self.lock:
            # Si llegamos al límite, eliminar la entrada más antigua
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]['created_at']
                )
                del self.cache[oldest_key]
            
            expires_at = None
            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            self.cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'expires_at': expires_at
            }
    
    def delete(self, key: str) -> None:
        """Elimina una entrada específica."""
        with self.lock:
            self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Limpia todo el caché."""
        with self.lock:
            self.cache.clear()
    
    def exists(self, key: str) -> bool:
        """Verifica existencia y validez de una clave."""
        return self.get(key) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del caché."""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'usage_percent': (len(self.cache) / self.max_size) * 100
            }


class CacheKeyGenerator:
    """Genera claves de caché consistentes y seguras."""
    
    @staticmethod
    def generate(
        namespace: str,
        identifier: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera una clave única basada en namespace, identificador y parámetros.
        
        Args:
            namespace: Categoría (ej: 'servicios', 'clientes')
            identifier: Identificador específico (ej: método o endpoint)
            params: Parámetros adicionales para hacer la clave única
        
        Returns:
            Clave segura y única
        """
        base = f"{namespace}:{identifier}"
        
        if params:
            params_str = json.dumps(params, sort_keys=True, default=str)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()
            return f"{base}:{params_hash}"
        
        return base


class CacheManager:
    """
    Gestor principal de caché con soporte para múltiples estrategias.
    Implementa patrón Singleton y Manager.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementa Singleton thread-safe."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de caché."""
        if self._initialized:
            return
        
        self.strategy: CacheStrategy = InMemoryCache(max_size=1000)
        self._initialized = True
    
    def set_strategy(self, strategy: CacheStrategy) -> None:
        """Permite cambiar la estrategia de caché (Open/Closed Principle)."""
        self.strategy = strategy
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché."""
        return self.strategy.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena valor en caché."""
        self.strategy.set(key, value, ttl)
    
    def delete(self, key: str) -> None:
        """Elimina valor del caché."""
        self.strategy.delete(key)
    
    def clear(self) -> None:
        """Limpia todo el caché."""
        self.strategy.clear()
    
    def exists(self, key: str) -> bool:
        """Verifica existencia."""
        return self.strategy.exists(key)
    
    def generate_key(
        self,
        namespace: str,
        identifier: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Genera claves consistentes."""
        return CacheKeyGenerator.generate(namespace, identifier, params)


def cached(
    namespace: str,
    ttl: int = 300,
    key_params: Optional[list] = None
):
    """
    Decorador para cachear resultados de funciones.
    Uso DRY para evitar repetir lógica de caché en múltiples funciones.
    
    Args:
        namespace: Categoría del caché
        ttl: Tiempo de vida en segundos
        key_params: Parámetros a incluir en la clave (nombres de argumentos)
    
    Ejemplo:
        @cached(namespace='servicios', ttl=600, key_params=['cedula'])
        def get_servicios_by_cedula(cedula):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_mgr = CacheManager()
            
            # Construir parámetros para la clave
            params = {}
            if key_params:
                # Obtener parámetros por nombre desde kwargs o posición
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                
                for param_name in key_params:
                    if param_name in kwargs:
                        params[param_name] = kwargs[param_name]
                    elif param_name in param_names:
                        idx = param_names.index(param_name)
                        if idx < len(args):
                            params[param_name] = args[idx]
            
            # Generar clave
            cache_key = cache_mgr.generate_key(
                namespace,
                func.__name__,
                params if params else None
            )
            
            # Intentar obtener del caché
            cached_value = cache_mgr.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_mgr.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(namespace: str, identifier: str = '*'):
    """
    Decorador para invalidar caché después de ejecutar una función.
    Útil para POST/PUT/DELETE que modifican datos.
    
    Args:
        namespace: Categoría de caché a invalidar
        identifier: Identificador específico o '*' para invalidar toda la categoría
    
    Ejemplo:
        @cache_invalidate(namespace='servicios')
        def crear_servicio(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            cache_mgr = CacheManager()
            if identifier == '*':
                # Invalidar toda la categoría (simular con patrón)
                # Para una solución más robusta, usar Redis con patrón matching
                cache_mgr.clear()
            else:
                key = cache_mgr.generate_key(namespace, identifier)
                cache_mgr.delete(key)
            
            return result
        
        return wrapper
    return decorator
