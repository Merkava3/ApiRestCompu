# Sistema de Caché - Documentación Completa

## 📋 Descripción General

Sistema de caché centralizado y eficiente que optimiza el rendimiento de la API REST eliminando consultas redundantes a la base de datos. Implementa **SOLID principles**, **patrones de diseño** y **código limpio**.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐          ┌──────────────────────────┐  │
│  │   Routers/      │          │  CacheMiddleware         │  │
│  │   Endpoints     ├──────────┤  - Intercepta peticiones │  │
│  │                 │          │  - Valida caché          │  │
│  └────────┬────────┘          └──────────────────────────┘  │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         @with_cache / @invalidate_cache             │   │
│  │              (Decoradores)                           │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         CacheManager (Singleton)                     │   │
│  │  - Gestiona instancia única de caché                │   │
│  │  - Genera claves consistentes                        │   │
│  │  - Administra estrategias                            │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     CacheStrategy (Interfaz Abstracta)              │   │
│  │  - get()                                             │   │
│  │  - set()                                             │   │
│  │  - delete()                                          │   │
│  │  - clear()                                           │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   InMemoryCache (Implementación Concreta)           │   │
│  │  - Thread-safe con RLock                            │   │
│  │  - Expiración TTL automática                        │   │
│  │  - Control de memoria con max_size                  │   │
│  │  - Estadísticas en tiempo real                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Módulos Principales

### 1. **cache_manager.py** - Gestor Central de Caché

#### Clases:

**`CacheStrategy`** (Interfaz Abstracta)
- Define contrato para todas las estrategias de caché
- Permite extensibilidad sin modificar código existente
- **SOLID**: Dependency Inversion Principle

```python
class CacheStrategy(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]: ...
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None): ...
    @abstractmethod
    def delete(self, key: str): ...
    @abstractmethod
    def clear(self): ...
    @abstractmethod
    def exists(self, key: str) -> bool: ...
```

**`InMemoryCache`** (Implementación Concreta)
- Caché en memoria con expiración TTL
- Thread-safe para entornos multi-threading
- Control automático de memoria

```python
cache = InMemoryCache(max_size=1000)
cache.set('key', value, ttl=300)  # 5 minutos
result = cache.get('key')
```

**`CacheKeyGenerator`** (Generador de Claves)
- Genera claves únicas y consistentes
- Hash MD5 para parámetros complejos
- Previene colisiones

```python
key = CacheKeyGenerator.generate(
    namespace='servicios',
    identifier='get_all',
    params={'estado': 'activo'}
)
# Resultado: 'servicios:get_all:abc123def456'
```

**`CacheManager`** (Singleton Pattern)
- Instancia única thread-safe
- Gestiona la estrategia de caché
- Permite cambiar estrategia en tiempo de ejecución

```python
mgr = CacheManager()  # Siempre la misma instancia
mgr.set('key', value)
result = mgr.get('key')
```

#### Decoradores:

**`@cached`** - Para métodos de modelo
```python
@cached(namespace='servicios', ttl=600, key_params=['cedula'])
def get_servicios_by_cedula(cedula):
    # Se cachea con clave única por cedula
    pass
```

**`@cache_invalidate`** - Invalidar caché
```python
@cache_invalidate(namespace='servicios')
def crear_servicio(data):
    # Invalida caché después de crear
    pass
```

---

### 2. **cache_config.py** - Configuración Centralizada

Define TTL por recurso y operación:

```python
CACHE_CONFIG = {
    'servicios': {
        'get_all': 600,          # 10 minutos
        'get_by_id': 600,
        'get_reporte': 900,      # 15 minutos
        'get_ultimo': 300,       # 5 minutos
    },
    'productos': {
        'get_all': 1800,         # 30 minutos
    },
    'inventario': {
        'get_all': 300,          # 5 minutos (datos volátiles)
    }
}
```

**Ventajas DRY**:
- TTL centralizado, no repetido en código
- Fácil de auditar y modificar
- Consistencia garantizada

---

### 3. **cache_middleware.py** - Middleware de Flask

**`CacheMiddleware`** - Gestión automática
- Intercepta peticiones GET (sin caché)
- Invalida caché en POST/PUT/DELETE
- Genera claves automáticamente

```python
cache_middleware = CacheMiddleware()
cache_middleware.init_app(app)
```

**Decoradores**:

**`@with_cache`** - Para endpoints GET
```python
@with_cache(resource='servicios', operation='get_all')
def get_servicios():
    # Se cachea automáticamente
    pass
```

**`@invalidate_cache`** - Para endpoints de modificación
```python
@invalidate_cache(resource='servicios')
def crear_servicio():
    # Invalida caché después
    pass
```

---

## 🔧 Instalación e Integración

### 1. Los archivos ya están creados en:
```
api/app/cache/
├── __init__.py
├── cache_manager.py
├── cache_config.py
└── cache_middleware.py
```

### 2. Integración en app/__init__.py
```python
from .cache import CacheMiddleware

def create_app(environment):
    # ... código existente ...
    
    # Inicializar caché
    cache_middleware = CacheMiddleware()
    cache_middleware.init_app(app)
    
    return app
```

### 3. Uso en routers (Ejemplo: servicios_routers.py)
```python
from ..cache import with_cache, invalidate_cache

# GET - Cachear
@servicios_routes.route('/servicios', methods=['GET'])
@with_cache(resource='servicios', operation='get_all')
def get_servicios():
    servicios = Servicios.get_servicio_all()
    return successfully(api_servicios_completos.dump(servicios))

# POST - Invalidar
@servicios_routes.route('/servicio', methods=['POST'])
@invalidate_cache(resource='servicios')
def post_client():
    # ... crear servicio ...
    return response(SUCCESSFULSERVICIO)
```

---

## 📊 Principios SOLID Aplicados

### **S**ingle Responsibility
- `CacheManager`: Gestiona caché
- `CacheStrategy`: Define interfaz
- `InMemoryCache`: Implementa almacenamiento
- `CacheKeyGenerator`: Genera claves
- `CacheMiddleware`: Intercepta peticiones

### **O**pen/Closed
- `CacheStrategy` permite nuevas implementaciones sin modificar existentes
- Redis, Memcached, etc., pueden agregarse sin cambios

```python
# Cambiar estrategia en tiempo de ejecución
mgr = CacheManager()
mgr.set_strategy(RedisCache())  # Implementación futura
```

### **L**iskov Substitution
- `InMemoryCache` puede reemplazar `CacheStrategy`
- Cualquier nueva implementación es intercambiable

### **I**nterface Segregation
- `CacheStrategy` solo expone métodos necesarios
- Clientes no dependen de detalles innecesarios

### **D**ependency Inversion
- Decoradores dependen de abstracciones (`CacheStrategy`)
- No acoplados a implementación específica

---

## 🎨 Patrones de Diseño Usados

### 1. **Singleton Pattern**
```python
class CacheManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```
**Uso**: Garantiza una única instancia de caché en toda la aplicación.

### 2. **Strategy Pattern**
```python
class CacheStrategy(ABC):
    @abstractmethod
    def get(self, key): ...

class InMemoryCache(CacheStrategy):
    def get(self, key):
        # Implementación específica
```
**Uso**: Permite cambiar estrategia de almacenamiento sin afectar código cliente.

### 3. **Decorator Pattern**
```python
@with_cache(resource='servicios', operation='get_all')
def get_servicios():
    # Agrega comportamiento de caché transparentemente
```
**Uso**: Añade caché sin modificar la función original.

### 4. **Factory Pattern** (en CacheManager)
```python
mgr = CacheManager()
key = mgr.generate_key(namespace, identifier, params)
```
**Uso**: Centraliza creación de claves e instancias.

---

## 💾 Características de Caché

### Expiración TTL Automática
```python
cache.set('key', value, ttl=300)  # Expira en 5 minutos
```
- Valores se eliminan automáticamente después de TTL
- Válido solo en el contexto de la petición actual

### Control de Memoria
```python
cache = InMemoryCache(max_size=1000)
```
- Máximo de 1000 entradas
- Elimina entrada más antigua cuando se alcanza límite
- Previene Memory Leaks

### Thread-Safe
```python
with self.lock:
    self.cache[key] = value
```
- Usa `threading.RLock()` para sincronización
- Seguro en entornos multi-threading

### Estadísticas
```python
stats = cache.get_stats()
# {
#   'size': 450,
#   'max_size': 1000,
#   'usage_percent': 45.0
# }
```

---

## 🚀 Casos de Uso

### 1. Cachear Reportes Complejos
```python
@servicios_routes.route('/servicio/reporte', methods=['GET'])
@with_cache(resource='servicios', operation='get_reporte', ttl=900)
def get_servicio_reporte():
    # Query compleja se ejecuta solo cada 15 minutos
    servicios = Servicios.get_servicio_reporte()
    return successfully(api_servicios_reporte.dump(servicios))
```

### 2. Cachear por Parámetro
```python
@servicios_routes.route('/servicio/<int:id>', methods=['GET'])
@with_cache(resource='servicios', operation='get_by_id', key_params=['id'])
def get_servicio(id):
    # Clave diferente por cada ID
    servicio = Servicios.get_servicio_filter(id_servicio=id)
    return successfully(api_servicio.dump(servicio))
```

### 3. Invalidación Automática
```python
@servicios_routes.route('/servicio', methods=['POST'])
@invalidate_cache(resource='servicios')
def crear_servicio():
    # Caché se limpia automáticamente después
    # Garantiza datos frescos
    pass
```

### 4. Caché Selectivo en Métodos
```python
from ..cache import cached

class Servicios:
    @staticmethod
    @cached(namespace='servicios', ttl=600, key_params=['cedula'])
    def get_servicios_by_cedula(cedula):
        # Se cachea solo para este método
        pass
```

---

## 📈 Impacto en Rendimiento

### Antes del Caché
```
100 peticiones GET /servicios
├─ 100 consultas a BD
├─ 100 * 50ms = 5000ms total
└─ Carga BD: Alta
```

### Después del Caché (TTL=600s)
```
100 peticiones GET /servicios
├─ 1 consulta a BD (primera petición)
├─ 99 hits de caché (< 1ms cada una)
├─ ~50ms + 99ms = ~150ms total
└─ Carga BD: 98% menos
```

**Mejora**: ~33x más rápido

---

## 🔍 Monitoreo

### Ver Estadísticas
```python
@app.route('/api/v1/cache/stats', methods=['GET'])
def cache_stats():
    mgr = CacheManager()
    if hasattr(mgr.strategy, 'get_stats'):
        return jsonify(mgr.strategy.get_stats())
    return {'status': 'stats not available'}
```

### Limpiar Caché
```python
@app.route('/api/v1/cache/clear', methods=['DELETE'])
def clear_cache():
    CacheManager().clear()
    return {'message': 'cache cleared'}
```

---

## 🛠️ Configuración Avanzada

### Ajustar TTL
En `cache_config.py`:
```python
CACHE_CONFIG = {
    'servicios': {
        'get_all': 300,  # Cambiar a 5 minutos
    }
}
```

### Cambiar Estrategia
```python
from api.app.cache import CacheManager, RedisCache

mgr = CacheManager()
mgr.set_strategy(RedisCache(host='localhost', port=6379))
```

### Deshabilitar Caché
En `cache_config.py`:
```python
CACHE_ENABLED = False
```

---

## 🐛 Troubleshooting

### Caché no se actualiza
- Verificar TTL en `cache_config.py`
- Asegurar `@invalidate_cache` en endpoints POST/PUT/DELETE
- Revisar si `CACHE_ENABLED=True`

### Memory leak
- Revisar `max_size` en `InMemoryCache`
- Usar `/api/v1/cache/stats` para monitorear
- Ajustar TTL más bajo si es necesario

### Datos inconsistentes
- Verificar que modificaciones usan `@invalidate_cache`
- No cachear funciones con side-effects
- Revisar timestamps en `cache.get_stats()`

---

## 📚 Referencias

- [Python ABCs](https://docs.python.org/3/library/abc.html)
- [Threading RLock](https://docs.python.org/3/library/threading.html#rlock)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Design Patterns](https://refactoring.guru/design-patterns)

---

## ✅ Checklist de Implementación

- [x] Crear módulo `cache/`
- [x] Implementar `CacheStrategy` (interfaz)
- [x] Implementar `InMemoryCache` (concreto)
- [x] Crear `CacheManager` (singleton)
- [x] Crear decoradores `@with_cache` y `@invalidate_cache`
- [x] Integrar `CacheMiddleware` en app
- [x] Aplicar decoradores en routers (servicios_routers.py)
- [x] Crear `cache_config.py` centralizada
- [x] Documentar patrones y casos de uso
- [ ] Implementar Redis para producción (futuro)
- [ ] Añadir endpoint de stats (futuro)
- [ ] Añadir endpoint de clear (futuro)

---

**Última actualización**: Enero 2026
**Versión**: 1.0
**Estado**: Producción
