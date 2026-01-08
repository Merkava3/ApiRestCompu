# 🧪 Guía de Testing - Manejo de Errores

## Cómo Probar el Nuevo Sistema de Errores

### 1. **Error de Conexión a Base de Datos**

**Cómo simular:**
- Detén el servicio PostgreSQL
- Haz una petición GET a cualquier endpoint

**Esperado (503):**
```json
{
  "code": 503,
  "success": false,
  "message": "Error de conexión con la base de datos. Por favor, intente nuevamente.",
  "error_type": "DATABASE_ERROR",
  "details": {
    "database_error": true
  }
}
```

**Log esperado:**
```
⚠️  ERROR DE BASE DE DATOS en 'get_servicios':
   Tipo: OperationalError
   Mensaje: SSL connection has been closed unexpectedly
```

---

### 2. **Violación de Restricción Única**

**Cómo simular:**
```bash
curl -X POST http://localhost:5000/api/v1/cliente \
  -H "Content-Type: application/json" \
  -d '{
    "cedula": "1234567890",
    "nombre": "Juan",
    "email": "duplicate@example.com"
  }'
```
(Ejecutar dos veces con el mismo email)

**Esperado (503):**
```json
{
  "code": 503,
  "success": false,
  "message": "El registro ya existe o viola una restricción de unicidad.",
  "error_type": "DATABASE_ERROR",
  "details": {
    "error_type": "INTEGRITY_ERROR",
    "details": "duplicate key..."
  }
}
```

---

### 3. **Validación Simple (Bad Request)**

**Cómo simular:**
```bash
curl -X POST http://localhost:5000/api/v1/servicio \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Esperado (400):**
```json
{
  "code": 400,
  "success": false,
  "message": "Bad request"
}
```

---

### 4. **Recurso No Encontrado (Not Found)**

**Cómo simular:**
```bash
curl -X GET http://localhost:5000/api/v1/cliente/99999
```

**Esperado (404):**
```json
{
  "code": 404,
  "success": false,
  "message": "Not found"
}
```

---

### 5. **Error Inesperado (Internal Server Error)**

**Cómo simular:**
- Provoca un error en el modelo (ej: división por cero)
- Usa un campo inválido que cause ValueError

**Esperado (500):**
```json
{
  "code": 500,
  "success": false,
  "message": "Error interno del servidor",
  "error_type": "ZeroDivisionError",
  "details": "division by zero"
}
```

**Log esperado:**
```
🔴 ERROR NO CONTROLADO en endpoint 'post_servicio':
   Tipo: ZeroDivisionError
   Mensaje: division by zero
   Stack Trace: [...]
```

---

## 📋 Checklist de Testing

### Test Básico
- [ ] GET a `/servicios` retorna 200
- [ ] POST inválido retorna 400
- [ ] GET a recurso inexistente retorna 404

### Test de Errores de BD
- [ ] Con BD desconectada → 503
- [ ] Con integridad violada → 503 + mensaje amigable
- [ ] Errores SQL no expuestos

### Test de Seguridad
- [ ] No aparece "SELECT ... FROM" en respuesta
- [ ] No aparece estructura de tablas
- [ ] No aparece stack trace detallado en usuario

### Test de Logging
- [ ] Los errores se registran en `logs/`
- [ ] Los logs contienen timestamp y endpoint
- [ ] Los logs tienen la información necesaria para debugging

---

## 🔍 Verificar Logs

Los logs se guardan en:
```
logs/api_errors.log
```

Revisar con:
```bash
# Windows PowerShell
Get-Content logs/api_errors.log -Tail 20

# Linux/Mac
tail -20 logs/api_errors.log
```

Esperado:
```
2025-01-08 14:30:45 - root - ERROR - Error de Base de Datos en get_servicios: OperationalError - SSL connection...
2025-01-08 14:31:10 - root - ERROR - Error inesperado en post_item: ValueError - ...
```

---

## 📊 Tabla de Códigos HTTP Esperados

| Escenario | Código | Mensaje |
|-----------|--------|---------|
| Éxito | 200 | (depende del endpoint) |
| Bad Request (validación) | 400 | Bad request |
| Not Found | 404 | Not found |
| Error BD (conexión) | 503 | Error de conexión con la BD |
| Error BD (integridad) | 503 | El registro ya existe |
| Error BD (otro) | 503 | Error al acceder a la BD |
| Error inesperado | 500 | Error interno del servidor |

---

## ✅ Validaciones de Seguridad

Asegúrate que NUNCA aparezcan en la respuesta:

```python
# ❌ NO DEBE APARECER
- "SELECT ... FROM"
- "psycopg2"
- "SQLAlchemy"
- "/path/to/file.py:123"
- "Traceback"
- Estructura de columnas de BD
- Nombres de tablas internas

# ✅ PUEDE APARECER
- "Error de conexión"
- "recurso no encontrado"
- "Campos requeridos faltantes"
- Mensajes amigables al usuario
```

---

## 🚀 Testing Automatizado

### Crear archivo `test_errors.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_connection_error():
    """Test error de conexión a BD"""
    response = requests.get(f"{BASE_URL}/servicios")
    
    # Si BD está caída, esperar 503
    if response.status_code == 503:
        data = response.json()
        assert data['error_type'] == 'DATABASE_ERROR'
        assert 'SELECT' not in data.get('details', '')
        print("✅ Error de conexión manejado correctamente")
    else:
        print("ℹ️  BD está disponible, saltando test")

def test_bad_request():
    """Test bad request"""
    response = requests.post(
        f"{BASE_URL}/servicio",
        json={},
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data['success'] == False
    print("✅ Bad request manejado correctamente")

def test_not_found():
    """Test not found"""
    response = requests.get(f"{BASE_URL}/cliente/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert data['success'] == False
    print("✅ Not found manejado correctamente")

if __name__ == '__main__':
    print("Iniciando tests...")
    test_bad_request()
    test_not_found()
    test_connection_error()
    print("\n✅ Todos los tests pasaron")
```

Ejecutar:
```bash
python test_errors.py
```

---

## 📈 Monitoreo en Producción

### Verificar Códigos HTTP
```bash
# Ver distribución de códigos HTTP
curl http://localhost:5000/api/v1/servicios -v 2>&1 | grep "< HTTP"
```

### Ver Respuestas de Error
```bash
# Simular error (detener BD)
curl -s http://localhost:5000/api/v1/servicios | jq .
```

### Análisis de Logs
```bash
# Contar errores por tipo
grep "ERROR" logs/api_errors.log | grep -o "error_type.*" | sort | uniq -c

# Ver errores en los últimos 5 minutos
grep "$(date -d '5 minutes ago' +'%Y-%m-%d %H:%M')" logs/api_errors.log
```

---

## 🎯 Criterios de Éxito

✅ Todos los endpoints retornan códigos HTTP correctos
✅ Los mensajes de error son amigables al usuario
✅ Los logs contienen detalles técnicos para debugging
✅ No se exponen detalles de BD en respuestas
✅ Los try-catch están eliminados de los routers
✅ El decorador @handle_endpoint_errors se usa en todos los endpoints GET/POST/PUT/DELETE

---

**¡Listo para testing!** 🧪
