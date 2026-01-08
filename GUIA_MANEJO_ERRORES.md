# 📋 Guía de Manejo Centralizado de Errores

## Descripción General

Se ha implementado un **sistema centralizado y optimizado** de manejo de errores en toda la API REST. Esto elimina redundancia de código y proporciona respuestas consistentes y profesionales.

---

## 🎯 Características Principales

### 1. **Decorador `@handle_endpoint_errors`**
Captura automáticamente:
- ✅ Errores de base de datos (conexión, operaciones SQL)
- ✅ Excepciones de API personalizadas
- ✅ Errores inesperados

```python
@app.route('/endpoint', methods=['GET'])
@handle_endpoint_errors
def get_endpoint():
    # El código SIN try-catch
    resultado = Modelo.get_data()
    return successfully(resultado)
```

### 2. **Decorador `@log_operation("Nombre Operación")`**
Registra el inicio y fin de operaciones importantes:

```python
@app.route('/crear', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Recurso")
def post_recurso():
    data = request.get_json(force=True)
    recurso = Modelo.new(data)
    if recurso.save():
        return response(schema.dump(recurso))
    return badRequest()
```

---

## 🚀 Cómo Usarlo

### Patrón Correcto (Código Limpio)

```python
from flask import Blueprint, request
from ..models import Modelo
from ..helpers.error_handler import handle_endpoint_errors, log_operation
from ..helpers.response import *

routes = Blueprint('routes', __name__)

@routes.route('/datos', methods=['GET'])
@handle_endpoint_errors
def get_datos():
    # El decorador capturará cualquier error
    datos = Modelo.get_all()
    return successfully(data.dump(datos))

@routes.route('/crear', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Item")
def post_item():
    json = request.get_json(force=True)
    if not json:
        return badRequest()  # Errores de validación simples
    
    item = Modelo.new(json)
    if item.save():
        return response(schema.dump(item))
    return badRequest()

@routes.route('/actualizar', methods=['PUT'])
@handle_endpoint_errors
@log_operation("Actualizar Item")
def put_item():
    json = request.get_json(force=True)
    item = Modelo.get(json.get('id'))
    
    if not item:
        return notFound()
    
    for key, value in json.items():
        setattr(item, key, value)
    
    if item.save():
        return update(schema.dump(item))
    return badRequest()
```

---

## ⚠️ Patrones a EVITAR

### ❌ INCORRECTO: Try-catch redundante

```python
@routes.route('/endpoint', methods=['GET'])
@handle_endpoint_errors
def get_endpoint():
    try:  # ← INNECESARIO, el decorador ya lo maneja
        resultado = Modelo.get_data()
        print(f"✅ Éxito: {resultado}")  # ← Eliminar prints
        return successfully(resultado)
    except Exception as e:  # ← REDUNDANTE
        print(f"❌ Error: {str(e)}")
        raise
```

### ❌ INCORRECTO: Logs con emojis en el código

```python
def endpoint():
    try:
        resultado = Modelo.get_data()
        print(f"❌ Error obteniendo datos: {str(e)}")  # ← ELIMINAR
        print(f"✅ Dato creado exitosamente")  # ← ELIMINAR
        raise
```

---

## 📊 Tipos de Errores Manejados Automáticamente

### 1. Errores de Conexión a Base de Datos (503)
```json
{
  "code": 503,
  "success": false,
  "message": "Error de conexión con la base de datos. Por favor, intente nuevamente.",
  "error_type": "DATABASE_ERROR"
}
```

### 2. Violación de Restricciones de Integridad (503)
```json
{
  "code": 503,
  "success": false,
  "message": "El registro ya existe o viola una restricción de unicidad.",
  "error_type": "DATABASE_ERROR"
}
```

### 3. Excepciones de API Personalizadas (400/500)
```python
# En tu código:
raise APIException(
    "Email ya registrado",
    status_code=400,
    details={"email": "usuario@example.com"}
)

# Respuesta:
{
  "code": 400,
  "success": false,
  "message": "Email ya registrado",
  "details": {"email": "usuario@example.com"}
}
```

### 4. Errores Inesperados (500)
```json
{
  "code": 500,
  "success": false,
  "message": "Error interno del servidor",
  "error_type": "ValueError",
  "details": "Descripción del error..."
}
```

---

## 🛠️ Validaciones Simples Sin Try-Catch

```python
@routes.route('/buscar', methods=['POST'])
@handle_endpoint_errors
def buscar():
    json = request.get_json(force=True)
    
    # Validación simple - retornar badRequest
    if not json or 'id' not in json:
        return badRequest()
    
    # El decorador capturará errores de BD
    resultado = Modelo.get(json['id'])
    
    if not resultado:
        return notFound()
    
    return successfully(schema.dump(resultado))
```

---

## 🔍 Configuración de Logging

Los errores se registran automáticamente en:
```
logs/api_errors.log
```

Con información detallada:
- Timestamp
- Endpoint que generó el error
- Tipo de error
- Stack trace

---

## ✅ Checklist para Nuevo Código

Antes de hacer push, verifica:

- [ ] ¿Usé `@handle_endpoint_errors`?
- [ ] ¿No hay try-catch innecesarios?
- [ ] ¿Eliminé todos los print() con emojis?
- [ ] ¿Los validaciones simples retornan `badRequest()`?
- [ ] ¿Los errores 404 retornan `notFound()`?
- [ ] ¿Los errores de lógica retornan `badRequest()` o `update()`?

---

## 📚 Funciones de Respuesta Disponibles

```python
from ..helpers.response import *

# Éxito (200)
response(data)           # Respuesta genérica
successfully(data)       # Respuesta con 'data'
update(data)             # Respuesta de actualización

# Errores del cliente (400)
badRequest(msg="")       # Solicitud malformada
notFound()               # Recurso no encontrado

# Errores del servidor (500)
# Mantenido automáticamente por @handle_endpoint_errors
```

---

## 🎓 Ejemplo Completo Limpio

```python
from flask import Blueprint, request
from ..models import Cliente
from ..helpers.error_handler import handle_endpoint_errors, log_operation
from ..helpers.response import *
from ..database.schemas import api_cliente

clientes = Blueprint('clientes', __name__)

@clientes.route('/clientes', methods=['GET'])
@handle_endpoint_errors
def get_clientes():
    """Obtiene todos los clientes"""
    clientes_list = Cliente.get_all()
    return successfully(api_cliente.dump(clientes_list))

@clientes.route('/cliente', methods=['POST'])
@handle_endpoint_errors
@log_operation("Crear Cliente")
def post_cliente():
    """Crea un nuevo cliente"""
    data = request.get_json(force=True)
    if not data:
        return badRequest()
    
    cliente = Cliente.new(data)
    if cliente.save():
        return response(api_cliente.dump(cliente))
    return badRequest()

@clientes.route('/cliente/<id>', methods=['GET'])
@handle_endpoint_errors
def get_cliente(id):
    """Obtiene un cliente por ID"""
    cliente = Cliente.get(id)
    if not cliente:
        return notFound()
    return successfully(api_cliente.dump(cliente))
```

---

## 📞 ¿Preguntas?

Revisa el archivo: `api/app/helpers/error_handler.py` para más detalles técnicos.
