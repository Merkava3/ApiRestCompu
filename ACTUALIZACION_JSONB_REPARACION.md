# 🔄 Actualización: Función JSONB para Insertar Reparación Completa

## ✅ Cambio Realizado

La función SQL `InsertarReparacionCompleta` ha sido refactorizada para usar **JSONB** en lugar de múltiples parámetros individuales.

---

## 📊 Comparativa

### ANTES ❌
```sql
CREATE OR REPLACE FUNCTION InsertarReparacionCompleta(
    p_id_reparacion BIGINT,
    p_estado VARCHAR(45),
    p_precio_reparacion DOUBLE PRECISION,
    p_descripcion TEXT,
    p_fecha_entrega TIMESTAMP,
    p_numero_serie VARCHAR(255),
    p_tipo VARCHAR(255) DEFAULT NULL,
    p_marca VARCHAR(255) DEFAULT NULL,
    p_modelo VARCHAR(255) DEFAULT NULL,
    p_reporte TEXT DEFAULT NULL,
    p_fecha_ingreso TIMESTAMP DEFAULT NULL,
    p_cedula VARCHAR(16),
    p_nombre_cliente VARCHAR(255) DEFAULT NULL,
    p_direccion TEXT DEFAULT NULL,
    p_telefono_cliente VARCHAR(50) DEFAULT NULL,
    p_dispositivo_id_reparacion BIGINT DEFAULT NULL
)
```

**Problemas:**
- 16 parámetros diferentes
- Difícil de mantener
- Fácil confundir el orden
- Validación complicada

---

### DESPUÉS ✅
```sql
CREATE OR REPLACE FUNCTION insertar_reparacion_completa(
    p_data JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
```

**Ventajas:**
- ✅ 1 parámetro único (JSONB)
- ✅ Fácil de mantener
- ✅ Flexible (campos opcionales)
- ✅ Mejor documentación
- ✅ Menos propenso a errores

---

## 📚 Uso desde Python

### ANTES ❌
```python
# Extraer múltiples parámetros
query_params = Help.extract_params(data, COLUMN_LIST_REPARACION_COMPLETA)
query = text(INSERTAR_REPARACION_COMPLETA)
db.session.execute(query, query_params)
```

### DESPUÉS ✅
```python
# Un parámetro JSON
import json
query = text(INSERTAR_REPARACION_COMPLETA)
db.session.execute(query, {"p_data": json.dumps(data)})
```

---

## 🔧 Archivos Actualizados

```
✅ postgresql/insertar_reparacion_completa.sql
   - Nueva función usando JSONB
   
✅ api/app/helpers/const.py
   - Constante SQL actualizada
   - COLUMN_LIST_REPARACION_COMPLETA simplificada
   
✅ api/app/models/reparaciones_model.py
   - Método insertar_reparacion_completa() refactorizado
```

---

## 📝 Formato de Datos Esperado

```python
data = {
    # Reparación (requerido)
    "id_reparacion": 1,
    "estado": "En proceso",
    "precio_reparacion": 50000.0,
    "descripcion": "Formateo del equipo",
    "fecha_entrega": "2025-12-01 00:00:00",
    
    # Dispositivo (requerido)
    "numero_serie": "SN123456",
    "tipo": "Celular",
    "marca": "Samsung",
    "modelo": "Galaxy S21",
    "reporte": "Pantalla rota",
    "fecha_ingreso": "2025-06-15 22:18:14",
    
    # Cliente (requerido)
    "cedula": "123456789",
    "nombre_cliente": "Juan Pérez",
    "direccion": "Calle Principal 123",  # Opcional
    "telefono_cliente": "+573001234567"   # Opcional
}

# Llamar
Reparaciones.insertar_reparacion_completa(data)
```

---

## ✨ Beneficios

### 1. **Flexibilidad**
- Campos opcionales fáciles de manejar
- Facilidad para agregar nuevos campos

### 2. **Mantenibilidad**
- Un único punto de cambio
- Código más limpio
- Menos propenso a errores

### 3. **Performance**
- Menos parámetros
- Mejor gestión de recursos
- Validación más eficiente

### 4. **Seguridad**
- Validación centralizada en SQL
- Mejor control de tipos

---

## 🚀 Validaciones en SQL

La función ahora valida automáticamente:

```sql
-- Campos requeridos
- id_reparacion
- cedula
- numero_serie (o dispositivo_id_reparacion)

-- Campos con valores por defecto
- estado → 'Pendiente'
- fecha_ingreso → NOW()
- descripcion → 'Sin descripción'
```

---

## 📋 Ejemplos de Uso

### Crear Reparación Completa
```python
@routes.route('/reparacion/insertar_completa', methods=['POST'])
@handle_endpoint_errors
def post_reparacion_completa():
    data = request.get_json(force=True)
    
    if Reparaciones.insertar_reparacion_completa(data):
        return response(SUCCESSFULREPARACION)
    return badRequest()
```

### Desde cURL
```bash
curl -X POST http://localhost:5000/api/v1/reparacion/insertar_completa \
  -H "Content-Type: application/json" \
  -d '{
    "id_reparacion": 1,
    "estado": "En proceso",
    "precio_reparacion": 50000,
    "descripcion": "Formateo",
    "fecha_entrega": "2025-12-01 00:00:00",
    "numero_serie": "SN123456",
    "tipo": "Celular",
    "marca": "Samsung",
    "modelo": "Galaxy S21",
    "cedula": "123456789",
    "nombre_cliente": "Juan Pérez"
  }'
```

---

## 🔍 Manejo de Errores

La función retorna:

```python
# Éxito
{
    "code": 200,
    "success": true,
    "message": "Reparación creada exitosamente"
}

# Error (validación)
{
    "code": 400,
    "success": false,
    "message": "id_reparacion es obligatorio"
}

# Error (BD)
{
    "code": 503,
    "success": false,
    "message": "Error de conexión con la base de datos"
}
```

---

## ✅ Checklist de Validación

- [x] Función SQL usando JSONB
- [x] Constante actualizada en const.py
- [x] Modelo Python refactorizado
- [x] Manejo centralizado de errores
- [x] Documentación completa
- [x] Compatible con decorador @handle_endpoint_errors

---

## 📞 Próximos Pasos

1. Ejecutar la función SQL en la BD
2. Probar el endpoint `/reparacion/insertar_completa`
3. Validar respuestas en todos los casos

---

## 💡 Ventajas de JSONB vs Parámetros

| Aspecto | Parámetros | JSONB |
|--------|-----------|-------|
| Cantidad de parámetros | 16 | 1 |
| Facilidad de uso | Media | Alta |
| Flexibilidad | Baja | Alta |
| Validación | Difícil | Centralizada |
| Mantenimiento | Difícil | Fácil |
| Performance | Normal | Optimizada |

---

**Refactorización completada.** ✨
