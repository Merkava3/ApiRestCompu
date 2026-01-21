"""
Guía de implementación del sistema de caché.
Muestra patrones y mejores prácticas.
"""

# ============================= EJEMPLO 1: Decorador @with_cache =============================
# Uso simple en routers para cachear respuestas GET

from flask import Blueprint
from ..cache import with_cache, invalidate_cache
from ..models import Servicios

servicios_routes = Blueprint('servicios', __name__)

# GET - Usar caché
@servicios_routes.route('/servicios', methods=['GET'])
@with_cache(resource='servicios', operation='get_all')
def get_servicios():
    """
    Obtiene todos los servicios.
    Se cachea durante 10 minutos según la configuración.
    """
    servicios = Servicios.get_servicio_all()
    return {'data': servicios}


@servicios_routes.route('/servicio/<int:servicio_id>', methods=['GET'])
@with_cache(resource='servicios', operation='get_by_id', key_params=['servicio_id'])
def get_servicio(servicio_id):
    """
    Obtiene un servicio específico.
    Se cachea pero con clave diferente por cada ID.
    """
    servicio = Servicios.get_servicio_filter(id_servicio=servicio_id)
    return {'data': servicio}


# POST/PUT/DELETE - Invalidar caché
@servicios_routes.route('/servicio', methods=['POST'])
@invalidate_cache(resource='servicios')
def crear_servicio():
    """
    Crea un nuevo servicio.
    Invalida automáticamente el caché de servicios.
    """
    # ... lógica de creación
    pass


@servicios_routes.route('/servicio/<int:servicio_id>', methods=['PUT'])
@invalidate_cache(resource='servicios')
def actualizar_servicio(servicio_id):
    """
    Actualiza un servicio.
    Invalida automáticamente el caché de servicios.
    """
    # ... lógica de actualización
    pass


# ============================= EJEMPLO 2: CacheManager directo =============================
# Uso avanzado cuando necesitas mayor control

from ..cache import CacheManager

def get_servicios_with_custom_logic():
    """
    Ejemplo de uso directo del CacheManager para lógica personalizada.
    """
    cache_mgr = CacheManager()
    
    # Generar clave personalizada
    cache_key = cache_mgr.generate_key(
        namespace='servicios',
        identifier='custom_logic',
        params={'estado': 'activo'}
    )
    
    # Intentar obtener del caché
    resultado = cache_mgr.get(cache_key)
    if resultado:
        return resultado
    
    # Si no está en caché, buscar en BD
    servicios = Servicios.get_servicio_all()
    
    # Almacenar en caché con TTL de 5 minutos
    cache_mgr.set(cache_key, servicios, ttl=300)
    
    return servicios


# ============================= EJEMPLO 3: @cached decorator =============================
# Uso en métodos de modelo para cachear operaciones complejas

from ..cache import cached
from flask_sqlalchemy import SQLAlchemy

class Servicios:
    @staticmethod
    @cached(namespace='servicios', ttl=600, key_params=['cedula'])
    def get_servicios_by_cedula(cedula):
        """
        Obtiene servicios de un cliente específico.
        Se cachea por cedula para evitar búsquedas repetidas.
        """
        # ... lógica de búsqueda en BD
        pass


# ============================= EJEMPLO 4: Estadísticas y Monitoreo =============================
# Obtener información del caché en tiempo real

def get_cache_stats():
    """Endpoint para monitorear el estado del caché."""
    cache_mgr = CacheManager()
    
    # Si la estrategia es InMemoryCache, obtener estadísticas
    if hasattr(cache_mgr.strategy, 'get_stats'):
        stats = cache_mgr.strategy.get_stats()
        return {
            'cache_size': stats['size'],
            'max_cache_size': stats['max_size'],
            'usage_percent': stats['usage_percent']
        }
    
    return {'status': 'cache strategy does not support stats'}


# ============================= EJEMPLO 5: Invalidación selectiva =============================
# Limpiar caché de forma granular

def invalidar_cache_servicio_especifico(servicio_id):
    """
    Invalida solo el caché de un servicio específico.
    Más eficiente que limpiar todo el caché.
    """
    cache_mgr = CacheManager()
    
    # Generar la clave exacta
    cache_key = cache_mgr.generate_key(
        namespace='servicios',
        identifier='get_by_id',
        params={'servicio_id': servicio_id}
    )
    
    # Eliminar solo esa entrada
    cache_mgr.delete(cache_key)


# ============================= MEJORES PRÁCTICAS =============================
"""
1. USAR @with_cache PARA ENDPOINTS:
   - Mantenimiento automático
   - TTL centralizado en cache_config.py
   - Menor acoplamiento

2. USAR @invalidate_cache EN MODIFICACIONES:
   - Garantiza datos frescos después de cambios
   - Automático y sin necesidad de lógica manual

3. USAR CacheManager DIRECTO PARA:
   - Lógica personalizada compleja
   - Invalidación selectiva
   - Estadísticas y monitoreo

4. CONFIGURAR TTL SEGÚN VOLATILIDAD:
   - Datos estáticos: 1800 seg (30 min)
   - Datos semi-estáticos: 600 seg (10 min)
   - Datos volátiles (inventario): 300 seg (5 min)
   - Datos muy volátiles: 60 seg (1 min)

5. MONITOREAR USO DE MEMORIA:
   - Revisar get_stats() regularmente
   - Ajustar max_size según necesidad
   - Considerar Redis para apps grandes

6. APLICAR PRINCIPIOS SOLID:
   - Single Responsibility: Cada clase tiene una responsabilidad
   - Open/Closed: Extensible sin modificar código existente
   - Dependency Inversion: Decoradores independientes de implementación
   - DRY: Código centralizado, sin repetición
"""
