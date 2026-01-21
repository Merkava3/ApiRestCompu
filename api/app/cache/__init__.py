"""
Init para el módulo de caché.
Exporta la interfaz pública.
"""
from .cache_manager import CacheManager, cached, cache_invalidate
from .cache_middleware import CacheMiddleware, with_cache, invalidate_cache
from .cache_config import CACHE_CONFIG, get_ttl, CACHE_ENABLED

__all__ = [
    'CacheManager',
    'cached',
    'cache_invalidate',
    'CacheMiddleware',
    'with_cache',
    'invalidate_cache',
    'CACHE_CONFIG',
    'get_ttl',
    'CACHE_ENABLED',
]
