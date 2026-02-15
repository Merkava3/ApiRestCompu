# Validación de Servicios - Documentación

## Descripción
El sistema de validación para servicios verifica que los datos cumplan con los formatos requeridos antes de insertarlos en la base de datos.

## Endpoint
**POST** `https://127.0.0.1:5000/api/v1/servicio/cliente`

## Reglas de Validación

| Campo | Regla | Ejemplo Válido | Ejemplo Inválido |
|-------|-------|----------------|------------------|
| `cedula` | Solo números | `"742742742"` | `"123ABC456"` |
| `nombre_cliente` | Solo letras con espacios | `"Homer Simpson"` | `"Homer123"` |
| `telefono_cliente` | Solo números | `"5559393"` | `"555-9393"` |
| `marca` | Solo letras (sin espacios) | `"KrustyBrand"` | `"Krusty Brand"` |
| `tipo_servicio` | Solo letras con espacios | `"Reparacion"` | `"Reparacion123"` |
| `modelo` | Letras, números y espacios (sin caracteres especiales) | `"K2000"` | `"K-2000@"` |
| `reporte` | Solo letras con espacios | `"Pantalla no enciende"` | `"Pantalla123"` |
| `precio_servicio` | Solo números | `150800` | `"150.80"` |

## Ejemplo de JSON Válido

```json
{
  "usuario_email": "lisa@planta742.com",
  "cedula": "742742742",
  "nombre_cliente": "Homer Simpson",
  "direccion": "742 Evergreen Terrace",
  "telefono_cliente": "5559393",
  "tipo": "Consola",
  "marca": "KrustyBrand",
  "modelo": "K2000",
  "numero_serie": "sn-4577677",
  "reporte": "Pantalla no enciende",
  "tipo_servicio": "Reparacion",
  "precio_servicio": 150800
}
```

## Ejemplo de JSON Inválido

```json
{
  "usuario_email": "lisa@planta742.com",
  "cedula": "742742742",
  "nombre_cliente": "Homer Simpson",
  "direccion": "742 Evergreen Terrace",
  "telefono_cliente": "555-9393",  // ERROR: contiene guión
  "tipo": "Consola",
  "marca": "KrustyBrand",
  "modelo": "K2000",
  "numero_serie": "sn-4577677",
  "reporte": "Pantalla no enciende",
  "tipo_servicio": "Reparacion",
  "precio_servicio": 150800
}
```

**Respuesta de error:**
```json
{
  "error": "El teléfono solo debe contener números"
}
```

## Respuestas del Servidor

### Validación Exitosa
**Código:** `200 OK`
```json
{
  "message": "Servicio creado exitosamente"
}
```

### Validación Fallida
**Código:** `400 Bad Request`
```json
{
  "error": "El teléfono solo debe contener números"
}
```

## Mensajes de Error Posibles

1. `"La cédula solo debe contener números"`
2. `"El nombre del cliente solo debe contener letras y espacios"`
3. `"El teléfono solo debe contener números"`
4. `"La marca solo debe contener letras (sin espacios)"`
5. `"El tipo de servicio solo debe contener letras y espacios"`
6. `"El modelo solo debe contener letras, números y espacios (sin caracteres especiales)"`
7. `"El reporte solo debe contener letras y espacios"`
8. `"El precio del servicio solo debe contener números"`

## Implementación Técnica

La validación se implementa en dos archivos:

### 1. `validator_input.py`
Contiene la clase `ValidatorInput` con el método `validate_service_input()` que valida todos los campos.

### 2. `servicios_routers.py`
El endpoint `/servicio/cliente` llama a la validación antes de insertar en la base de datos:

```python
@servicios_routes.route('/servicio/cliente', methods=['POST'])
@handle_endpoint_errors
@log_operation("Insertar con Cliente")
def create_with_client():
    """Insertar servicio junto con datos de cliente."""
    data = request.get_json(force=True)
    if not data: return badRequest(ERROR)
    
    # Validar los datos de entrada
    is_valid, error_message = ValidatorInput.validate_service_input(data)
    if not is_valid:
        return badRequest(error_message)
    
    Help.add_generated_id_to_data(data, ID_SERVICIO)
    Help.add_default_value_to_data(data, 'estado_servicio', 'recibido')
    if Servicios.insertar_servicio(data):
        return response(SUCCESSFULSERVICIO)
    return badEquals()
```

## Pruebas

Para ejecutar las pruebas de validación:

```bash
cd e:\javascripts\ApiRestCompu\api
python test_validation_servicio.py
```

Este script de prueba valida:
- El JSON de ejemplo con el error en `telefono_cliente`
- El JSON corregido con todos los datos válidos
- Casos individuales de error para cada campo
