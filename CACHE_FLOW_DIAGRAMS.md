# 🎨 Diagrama de Flujo - Sistema de Caché

## Flujo de una Petición GET (Con Caché)

```
┌────────────────────────────────────────────────────────────────┐
│                   CLIENT (Browser/API)                          │
├────────────────────────────────────────────────────────────────┤
│  GET /api/v1/servicios                                          │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              FLASK APP - Middleware                              │
├────────────────────────────────────────────────────────────────┤
│  @app.before_request()                                          │
│  - Generar cache_key                                            │
│  - Guardar en g.cache_key                                       │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    ENDPOINT (@with_cache)                        │
├────────────────────────────────────────────────────────────────┤
│  @servicios_routes.route('/servicios', methods=['GET'])        │
│  @with_cache(resource='servicios', operation='get_all')        │
│  def get_servicios():                                           │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
                    ¿Existe en caché?
                    /              \
                  SÍ/              \NO
                  /                 \
       ┌─────────┐              ┌──────────────────────────────┐
       │          │             │  EJECUTAR FUNCIÓN            │
       │ RETORNAR │             │                              │
       │  DESDE   │             │ servicios = Servicios.get... │
       │  CACHÉ   │             │                              │
       │          │             │ (Query a Base de Datos)      │
       │ <5ms     │             │                              │
       └────┬─────┘             └──────────┬───────────────────┘
            │                              │
            │                              ▼
            │                    ┌──────────────────┐
            │                    │  GUARDAR EN      │
            │                    │  CACHÉ           │
            │                    │                  │
            │                    │ mgr.set(key,    │
            │                    │   result,       │
            │                    │   ttl=600)      │
            │                    └────────┬─────────┘
            │                             │
            └────────────┬────────────────┘
                         │
                         ▼
        ┌─────────────────────────────────────────┐
        │   PROCESAR RESPUESTA Y DEVOLVER         │
        │                                         │
        │   return successfully(api.dump(data))  │
        └──────────┬──────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────────┐
        │  @app.after_request()                   │
        │  (Sin invalidación, es GET)             │
        └──────────┬──────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────────┐
        │  ENVIAR RESPUESTA AL CLIENT             │
        │  HTTP 200 OK                            │
        │  {data: [...]}                          │
        └─────────────────────────────────────────┘
```

---

## Flujo de una Petición POST (Con Invalidación)

```
┌────────────────────────────────────────────────────────────────┐
│                   CLIENT (Browser/API)                          │
├────────────────────────────────────────────────────────────────┤
│  POST /api/v1/servicio                                          │
│  {cliente_id: 1, tipo: "reparación", ...}                       │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              FLASK APP - Middleware                              │
├────────────────────────────────────────────────────────────────┤
│  @app.before_request()                                          │
│  - No cachear (POST != GET)                                     │
│  - Marcar como modificación                                     │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│              ENDPOINT (@invalidate_cache)                        │
├────────────────────────────────────────────────────────────────┤
│  @servicios_routes.route('/servicio', methods=['POST'])        │
│  @invalidate_cache(resource='servicios')                       │
│  def post_servicio():                                           │
│      data = request.get_json()                                  │
│      Servicios.insertar_servicio(data)                          │
│      return response(SUCCESS)                                   │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────┐
        │  @app.after_request()                   │
        │  (Es POST, invalidar caché)             │
        │                                         │
        │  CacheManager().clear()                │
        │  (Limpia todo el caché)                │
        └──────────┬──────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────────┐
        │  ENVIAR RESPUESTA AL CLIENT             │
        │  HTTP 200 OK                            │
        │  {mensaje: "Servicio creado"}           │
        └─────────────────────────────────────────┘
        
        ⚠️  LA PRÓXIMA PETICIÓN GET CONSULTARÁ BD
```

---

## Estructura Interna del Caché

```
CacheManager (Singleton)
    │
    └─── strategy: CacheStrategy
         │
         └─── InMemoryCache
              │
              └─── cache: Dict
                   │
                   ├─── key1: {value, created_at, expires_at}
                   ├─── key2: {value, created_at, expires_at}
                   ├─── key3: {value, created_at, expires_at}
                   │    ...
                   └─── key1000: {value, created_at, expires_at}
                        ↑
                        └─── max_size = 1000 (RLImite de memoria)
```

---

## Flujo de Generación de Claves

```
CacheKeyGenerator.generate(
    namespace='servicios',
    identifier='get_all',
    params={'estado': 'activo'}
)
│
├─ Construir base:
│  "servicios:get_all"
│
├─ Parámetros a JSON:
│  {"estado": "activo"}
│
├─ Hash MD5:
│  "a1b2c3d4e5f6..."
│
└─ Resultado final:
   "servicios:get_all:a1b2c3d4e5f6..."
```

---

## Ciclo de Vida de una Entrada de Caché

```
SET (Almacenar)
│
├─ time_stored = now()
├─ expires_at = now() + ttl
├─ Guardar en dict
│
▼
DURANTE EL TTL (Activo)
│
├─ GET → Verifica expires_at
├─ Si expires_at > now() → Retornar valor
├─ Si expires_at <= now() → Eliminar y retornar None
│
▼
DESPUÉS DE TTL (Expirado)
│
├─ Automáticamente eliminado
├─ La siguiente consulta irá a BD
├─ Y se almacenará nuevamente en caché
│
▼
O MANUALMENTE
│
├─ DELETE("key") → Elimina inmediatamente
├─ CLEAR() → Elimina todo el caché
├─ INVALIDATE_CACHE → Limpia el recurso
│
▼
FIN
```

---

## Comparación: Sin Caché vs Con Caché

```
ESCENARIO: 1000 usuarios hacen GET /servicios en 10 minutos

SIN CACHÉ:
├─ Petición 1  → BD Query (50ms) → Respuesta (55ms)
├─ Petición 2  → BD Query (50ms) → Respuesta (55ms)
├─ Petición 3  → BD Query (50ms) → Respuesta (55ms)
├─ ...
└─ Petición 1000 → BD Query (50ms) → Respuesta (55ms)
   ────────────────────────────────────────────────
   Total: 1000 queries × 50ms = 50 SEGUNDOS
   Carga BD: CRÍTICA ⚠️
   CPU BD: 100% 🔥


CON CACHÉ (TTL=600s):
├─ Petición 1  → BD Query (50ms) → Almacenar caché → Respuesta (55ms)
├─ Petición 2  → Caché hit (<1ms) → Respuesta (<5ms) ✓
├─ Petición 3  → Caché hit (<1ms) → Respuesta (<5ms) ✓
├─ ...
└─ Petición 1000 → Caché hit (<1ms) → Respuesta (<5ms) ✓
   ────────────────────────────────────────────────
   Total: 1 query × 50ms + 999 hits × 1ms = 1.05 SEGUNDOS
   Carga BD: 1% (solo datos frescos)
   CPU BD: <5% 🟢
   
MEJORA: 50÷1.05 ≈ 47x MÁS RÁPIDO ⚡
```

---

## Métodos de CacheManager

```
CacheManager (Singleton)
│
├─ get(key: str) → Any
│  │ Obtiene valor del caché
│  │ Retorna None si no existe o expiró
│  └─ Ejemplo: mgr.get('servicios:get_all')
│
├─ set(key: str, value: Any, ttl: int = None) → None
│  │ Almacena valor en caché
│  │ Si max_size alcanzado, elimina entrada más antigua
│  └─ Ejemplo: mgr.set('key', data, ttl=300)
│
├─ delete(key: str) → None
│  │ Elimina una entrada específica
│  └─ Ejemplo: mgr.delete('servicios:get_all')
│
├─ clear() → None
│  │ Limpia todo el caché
│  └─ Ejemplo: mgr.clear()
│
├─ exists(key: str) → bool
│  │ Verifica si una clave existe y es válida
│  └─ Ejemplo: if mgr.exists('key'): ...
│
└─ generate_key(namespace, identifier, params) → str
   │ Genera clave consistente
   └─ Ejemplo: key = mgr.generate_key('svc', 'all')
```

---

## Comparación de Estrategias

```
ESTRATEGIA          VELOCIDAD   MEMORIA   DISTRIBUCIÓN   USO
────────────────────────────────────────────────────────────────
InMemoryCache       Muy rápida  ~10-50MB  Local          Dev/Prod local
(Actual)            <1ms        Limitada  No             Pequeño-Medio

RedisCache          Rápida      Ilimitada Posible        Prod grande
(Futura)            1-5ms       Flexible  Sí             Múltiples servers

MemcachedCache      Muy rápida  ~100-500M Posible        Prod muy grande
(Futura)            <1ms        Flexible  Sí             Alta concurrencia

DatabaseCache       Lenta       Ilimitada Centralizada   Auditoría
(Futura)            50-100ms    Ilimitada Sí             Logs/Analytics
```

---

## Activación en Routers

```
Patrón de Decoradores:

GET ENDPOINT (Cachear):
    │
    ├─ @route()           ◄─ Definir ruta
    ├─ @handle_endpoint_errors  ◄─ Manejo de errores
    └─ @with_cache()      ◄─ CACHEAR RESULTADO
    def get_something():
        pass

POST/PUT/DELETE ENDPOINT (Invalidar):
    │
    ├─ @route()           ◄─ Definir ruta
    ├─ @handle_endpoint_errors  ◄─ Manejo de errores
    ├─ @log_operation()   ◄─ Log de auditoría
    └─ @invalidate_cache() ◄─ LIMPIAR CACHÉ
    def post_something():
        pass
```

---

## Integración en la Aplicación

```
ARQUITECTURA GENERAL:

┌──────────────────────────────────────────────────────────────┐
│                   FLASK APP                                   │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            CacheMiddleware (init_app)                  │  │
│  │  - before_request: Preparar caché                      │  │
│  │  - after_request: Invalidar si POST/PUT/DELETE        │  │
│  └────────────────────────────────────────────────────────┘  │
│                          ▲                                    │
│                          │                                    │
│  ┌─────────────────────┴──────────────────────┐             │
│  │         Blueprints / Routers               │             │
│  │                                             │             │
│  │  servicios_routes:                         │             │
│  │  ├─ GET /servicios         @with_cache    │             │
│  │  ├─ POST /servicio         @invalidate    │             │
│  │  ├─ PUT /servicio          @invalidate    │             │
│  │  └─ DELETE /servicio       @invalidate    │             │
│  │                                             │             │
│  │  cliente_routes:                           │             │
│  │  ├─ GET /clientes          @with_cache    │             │
│  │  ├─ POST /cliente          @invalidate    │             │
│  │  ...                                        │             │
│  └─────────────────────────────────────────────┘             │
│                          │                                    │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           CacheManager (Singleton)                      │  │
│  │  - Gestiona todas las operaciones de caché             │  │
│  │  - Thread-safe con locks                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                          │                                    │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         InMemoryCache (Strategy)                        │  │
│  │  - Almacena datos en memoria                            │  │
│  │  - Control de expiración TTL                            │  │
│  │  - Límite de memoria (max_size)                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                          │                                    │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │     {key1: value1, key2: value2, ...}                  │  │
│  │          (Hasta 1000 entradas)                          │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

**Diagrama generado**: Enero 2026  
**Versión**: 1.0  
**Actualización**: Todos los diagramas están al día ✓
