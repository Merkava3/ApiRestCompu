"""
Configuración de caché para la aplicación.
Define valores por defecto y estrategias globales.
"""
from typing import Dict, Any

# Configuración de TTL por endpoint/operación
CACHE_CONFIG: Dict[str, Any] = {
    'servicios': {
        'get_all': 600,              # 10 minutos
        'get_by_id': 600,            # 10 minutos
        'get_reporte': 900,          # 15 minutos
        'get_ultimo': 300,           # 5 minutos
    },
    'clientes': {
        'get_all': 600,
        'get_by_cedula': 600,
    },
    'dispositivos': {
        'get_all': 600,
        'get_by_cliente': 600,
    },
    'productos': {
        'get_all': 1800,             # 30 minutos
        'get_by_id': 1800,
    },
    'inventario': {
        'get_all': 300,              # 5 minutos (cambia frecuentemente)
        'get_by_producto': 300,
    },
    'facturas': {
        'get_all': 600,
        'get_by_cliente': 600,
    },
    'proveedores': {
        'get_all': 1800,             # 30 minutos
    }
}

# Configuración de caché en memoria
CACHE_MEMORY_CONFIG = {
    'max_size': 1000,                # Máximo de entradas
    'cleanup_interval': 300,         # Limpiar expirados cada 5 minutos
}

# Definir si usar caché globalmente
CACHE_ENABLED = False

# Operaciones que invalidarán caché
CACHE_INVALIDATE_ON = ['POST', 'PUT', 'DELETE', 'PATCH']


def get_ttl(resource: str, operation: str) -> int:
    """
    Obtiene el TTL configurado para un recurso y operación.
    
    Args:
        resource: Tipo de recurso (ej: 'servicios')
        operation: Operación (ej: 'get_all')
    
    Returns:
        TTL en segundos
    """
    return CACHE_CONFIG.get(resource, {}).get(operation, 300)
