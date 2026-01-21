# Diagnóstico de Errores CORS y 500

## ✅ Cambios Realizados

### 1. **Configuración CORS Mejorada** (`api/app/__init__.py`)
- Ahora permite múltiples métodos: GET, POST, PUT, DELETE, OPTIONS, PATCH
- Permitidos headers: Content-Type, Authorization
- Configurable para localhost en desarrollo
- Max-age aumentado a 3600 segundos

### 2. **Orígenes CORS Permitidos** (`api/config.py`)
- `http://localhost:3000` ✅
- `http://localhost:5000` ✅
- `http://127.0.0.1:3000` ✅
- `http://127.0.0.1:5000` ✅
- `*` (wildcard) ✅

### 3. **Endpoint de Verificación** (`api/app/views.py`)
- Agregado endpoint `/api/v1/health` para verificar que el servidor funciona
- Prueba CORS sin acceder a base de datos

---

## 🔍 Pasos para Diagnosticar Errores

### Paso 1: Verificar que el servidor está corriendo
```bash
# Terminal del backend
python api/main.py
```

Deberías ver:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Paso 2: Probar el endpoint de salud
```bash
# En otra terminal
curl -X GET http://127.0.0.1:5000/api/v1/health
```

Respuesta esperada:
```json
{
  "status": "ok",
  "message": "Servidor funcionando correctamente"
}
```

Si recibest error CORS aquí, es un problema de configuración.
Si recibas error 500, revisa la consola del backend.

### Paso 3: Si hay error en consola del navegador (CORS)
Mira la consola del navegador (F12 → Consola) para ver el error exacto:
- **CORS error**: El servidor no está permitiendo la solicitud
- **Network tab**: Verifica el estado HTTP de la solicitud (preflight OPTIONS)

### Paso 4: Si hay error 500 en el backend
Revisa la consola de Python donde corre `python api/main.py`:

**Ejemplo de error común:**
```
🔴 ERROR NO CONTROLADO en endpoint 'get_servicio_reporte':
   Tipo: AttributeError
   Mensaje: 'NoneType' object has no attribute 'all'
```

Esto significa que una consulta devolvió None.

---

## 🛠️ Soluciones Comunes

### Error: `CORS policy: Response to preflight request doesn't pass access control check`

**Causa:** El servidor no está respondiendo correctamente a solicitudes OPTIONS

**Solución:**
```python
# Asegúrate de que en __init__.py tengas esto:
CORS(
    app,
    origins=app.config.get('CORS_ORIGINS', ['*']),
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allow_headers=['Content-Type', 'Authorization'],
    supports_credentials=True,
    max_age=3600
)
```

### Error: `TypeError: 'NoneType' object has no attribute 'all'`

**Causa:** Estás intentando llamar `.all()` en una variable None

**Solución:** Verifica que tu consulta devuelva un objeto Query:
```python
# ❌ Malo
query = None
results = query.all()  # TypeError

# ✅ Bueno
if results:
    mapped = Help.map_query_results(results, CAMPOS_SERVICIO_REPORTE)
    return mapped
return []
```

### Error: `IndexError: tuple index out of range`

**Causa:** El número de columnas en la consulta no coincide con los campos en CAMPOS_*

**Solución:** Cuenta los campos:
```python
# En const.py - Contar campos
CAMPOS_SERVICIO_REPORTE = (
    "id_servicio",        # 1
    "cedula",             # 2
    "nombre_cliente",     # 3
    "telefono_cliente",   # 4
    "fecha_ingreso",      # 5
    "tipo_servicio"       # 6
)

# En servicio_model.py - Contar columnas en query
query = db.session.query(
    Servicios.id_servicio,              # 1
    Cliente.cedula,                     # 2
    Cliente.nombre_cliente,             # 3
    Cliente.telefono_cliente,           # 4
    Dispositivo.fecha_ingreso,          # 5
    Servicios.tipo_servicio             # 6
)
# Total: 6 = 6 ✅
```

---

## 📋 Checklist de Verificación

- [ ] Servidor Flask corre sin errores
- [ ] `/api/v1/health` devuelve 200 OK
- [ ] CORS permite peticiones desde localhost
- [ ] Headers de CORS correctos en respuesta
- [ ] Base de datos está conectada
- [ ] No hay errores en consola de Python
- [ ] Consultas SQL devuelven datos

---

## 📞 Información de Debug

### Variables de Entorno (opcional)
```bash
# Para sobrescribir los CORS permitidos
export CORS_ORIGINS="http://localhost:3000,http://localhost:5000,*"

# Para cambiar entorno
export FLASK_ENV=development
```

### Logs Detallados
En `error_handler.py`, los errores se imprimen en consola con formato:
- `❌ API Error` - Error controlado
- `⚠️  ERROR DE BASE DE DATOS` - Error de BD
- `🔴 ERROR NO CONTROLADO` - Excepción inesperada

---

## 🚀 Próximos Pasos

1. Prueba el endpoint `/api/v1/health` desde el navegador o Postman
2. Si funciona, intenta con otro endpoint (ej: `/api/v1/servicios`)
3. Revisa la consola de Python para errores 500
4. Si hay errores, copia el stack trace y revisa qué hace exactamente

Cualquier error específico, compártelo y lo debugueamos juntos.
