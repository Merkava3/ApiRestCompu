# ⚡ Quick Reference - Manejo de Errores

## 🎯 Reglas de Oro

### 1️⃣ Usa `@handle_endpoint_errors` en TODO endpoint
```python
@routes.route('/endpoint', methods=['GET', 'POST', 'PUT', 'DELETE'])
@handle_endpoint_errors  # ← SIEMPRE
def mi_endpoint():
    pass
```

### 2️⃣ NO hagas try-catch dentro de la función
```python
# ❌ MAL
@handle_endpoint_errors
def endpoint():
    try:  # ← NO HACER
        pass
    except:  # ← NO HACER
        pass

# ✅ BIEN
@handle_endpoint_errors
def endpoint():
    # Solo código de lógica
    pass
```

### 3️⃣ Elimina todos los `print()` con emojis
```python
# ❌ MAL
print(f"❌ Error obteniendo datos")
print(f"✅ Dato creado")

# ✅ BIEN
# (Sin prints - el decorador maneja logging)
```

### 4️⃣ Usa decoradores en el orden correcto
```python
@routes.route('/endpoint', methods=['POST'])
@handle_endpoint_errors
@log_operation("Mi Operación")
def endpoint():
    pass
```

---

## 📝 Plantilla Básica

```python
from flask import Blueprint, request
from ..models import MiModelo
from ..helpers.error_handler import handle_endpoint_errors, log_operation
from ..helpers.response import *
from ..database.schemas import api_schema

routes = Blueprint('mi_routes', __name__)

# GET - Listar
@routes.route('/items', methods=['GET'])
@handle_endpoint_errors
def get_items():
    items = MiModelo.get_all()
    return successfully(api_schema.dump(items))

# GET - Obtener uno
@routes.route('/item/<id>', methods=['GET'])
@handle_endpoint_errors
def get_item(id):
    item = MiModelo.get(id)
    if not item:
        return notFound()
    return successfully(api_schema.dump(item))

# POST - Crear
@routes.route('/item', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Item")
def post_item():
    data = request.get_json(force=True)
    if not data:
        return badRequest()
    item = MiModelo.new(data)
    if item.save():
        return response(api_schema.dump(item))
    return badRequest()

# PUT - Actualizar
@routes.route('/item/<id>', methods=['PUT'])
@handle_endpoint_errors
@log_operation("Actualizar Item")
def put_item(id):
    item = MiModelo.get(id)
    if not item:
        return notFound()
    data = request.get_json(force=True)
    for key, value in data.items():
        setattr(item, key, value)
    if item.save():
        return update(api_schema.dump(item))
    return badRequest()

# DELETE - Eliminar
@routes.route('/item/<id>', methods=['DELETE'])
@handle_endpoint_errors
@log_operation("Eliminar Item")
def delete_item(id):
    item = MiModelo.get(id)
    if not item:
        return notFound()
    if item.delete():
        return delete()
    return badRequest()
```

---

## 🚨 Respuestas Permitidas

```python
from ..helpers.response import *

# ✅ Éxito (200)
response(data)              # Crear/Genérico
successfully(data)          # Obtener/Listar
update(data)               # Actualizar
delete()                   # Eliminar

# ✅ Error del Cliente (400)
badRequest()               # Validación, formato inválido
badRequest("mensaje")      # Con mensaje custom
notFound()                 # Recurso no existe

# ✅ Errores de BD (Automáticos)
# El @handle_endpoint_errors retorna:
# - 503 para errores de conexión
# - 503 para violación de integridad
# - 500 para otros errores inesperados
```

---

## 🔍 Patrones a Reconocer

### Validación Simple
```python
# ✅ CORRECTO
if not data or 'email' not in data:
    return badRequest()

# ❌ NO HACER
if not data or 'email' not in data:
    raise APIException("Email faltante", 400)  # Innecesario
```

### Búsqueda de Recurso
```python
# ✅ CORRECTO
item = MiModelo.get(id)
if not item:
    return notFound()

# ❌ NO HACER
try:
    item = MiModelo.get(id)
except:
    return notFound()  # Innecesario, @handle_endpoint_errors lo maneja
```

### Operación de Base de Datos
```python
# ✅ CORRECTO
if item.save():  # El @handle_endpoint_errors captura errores BD
    return response(data)
return badRequest()

# ❌ NO HACER
try:
    if item.save():
        return response(data)
except Exception as e:  # Redundante
    raise
```

---

## 📊 Códigos HTTP Esperados

| Caso | Código | Función | Uso |
|------|--------|---------|-----|
| Éxito | 200 | `response()`, `successfully()` | Operación exitosa |
| Error validación | 400 | `badRequest()` | Input inválido |
| No encontrado | 404 | `notFound()` | ID no existe |
| Error BD conexión | 503 | Auto (decorador) | BD desconectada |
| Error BD integridad | 503 | Auto (decorador) | Constraint violation |
| Error inesperado | 500 | Auto (decorador) | Bug en código |

---

## 🛠️ Debug

### Ver Error en Consola
```
⚠️  ERROR DE BASE DE DATOS en 'post_item':
   Tipo: OperationalError
   Mensaje: SSL connection has been closed unexpectedly
```

### Ver en Response
```json
{
  "code": 503,
  "message": "Error de conexión con la base de datos. Por favor, intente nuevamente.",
  "error_type": "DATABASE_ERROR"
}
```

### Ver en Logs
```bash
# Windows
Get-Content logs/api_errors.log -Tail 10

# Linux
tail -10 logs/api_errors.log
```

---

## ✅ Checklist Antes de Commit

- [ ] ¿Usé `@handle_endpoint_errors`?
- [ ] ¿No hay try-catch innecesarios?
- [ ] ¿Eliminé todos los print()?
- [ ] ¿Retorno `badRequest()` para validaciones?
- [ ] ¿Retorno `notFound()` cuando no existe?
- [ ] ¿Retorno `response()` para crear?
- [ ] ¿Retorno `update()` para actualizar?
- [ ] ¿Retorno `delete()` para eliminar?

---

## 🎓 Recurso Principal

**Para más información:** [GUIA_MANEJO_ERRORES.md](GUIA_MANEJO_ERRORES.md)

---

**Mantén el código limpio. Usa `@handle_endpoint_errors`. ✨**
