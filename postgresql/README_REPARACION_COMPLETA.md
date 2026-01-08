# Procedimiento Almacenado: InsertarReparacionCompleta

## 📋 Descripción

Procedimiento almacenado mejorado que inserta una reparación completa manejando cliente, dispositivo y reparación en una sola transacción. Está alineado con el ORM de Python y el JSON proporcionado.

## ✨ Características

- ✅ **Manejo completo de relaciones**: Cliente → Dispositivo → Reparación
- ✅ **Búsqueda o creación automática**: Busca clientes por cédula y dispositivos por número de serie
- ✅ **Actualización automática**: Si el dispositivo existe, puede actualizar sus datos
- ✅ **Transaccional**: Todo se ejecuta en una sola transacción (all or nothing)
- ✅ **Validaciones robustas**: Valida parámetros requeridos
- ✅ **Manejo de errores**: Captura y reporta errores específicos

## 📊 Estructura del JSON de Entrada

El JSON debe incluir los siguientes campos según el ORM:

```json
{
    "id_reparacion": 1,
    "estado": "En proceso",
    "precio_reparacion": 50000.0,
    "descripcion": "formateo del equipo",
    "fecha_entrega": "2023-12-01T00:00:00",
    "numero_serie": "SN123456",
    "tipo": "Celular",
    "marca": "Samsung",
    "modelo": "Galaxy S21",
    "reporte": "Pantalla rota",
    "fecha_ingreso": "2025-06-15T22:18:14.658067",
    "cedula": "123456789",
    "nombre_cliente": "Juan Pérez",
    "direccion": "Calle 123",
    "telefono_cliente": "555-1234",
    "dispositivo_id_reparacion": null  // Opcional: si ya existe el dispositivo
}
```

## 🔧 Parámetros del Procedimiento

### Parámetros Requeridos
- `p_id_reparacion`: ID de la reparación (BIGINT)
- `p_estado`: Estado de la reparación (VARCHAR(45))
- `p_precio_reparacion`: Precio de la reparación (DOUBLE PRECISION)
- `p_descripcion`: Descripción de la reparación (TEXT)
- `p_fecha_entrega`: Fecha de entrega (TIMESTAMP)
- `p_numero_serie`: Número de serie del dispositivo (VARCHAR(255))
- `p_cedula`: Cédula del cliente (VARCHAR(16))

### Parámetros Opcionales (Dispositivo)
- `p_tipo`: Tipo de dispositivo (VARCHAR(255), default: NULL)
- `p_marca`: Marca del dispositivo (VARCHAR(255), default: NULL)
- `p_modelo`: Modelo del dispositivo (VARCHAR(255), default: NULL)
- `p_reporte`: Reporte del dispositivo (TEXT, default: NULL)
- `p_fecha_ingreso`: Fecha de ingreso del dispositivo (TIMESTAMP, default: NULL)

### Parámetros Opcionales (Cliente)
- `p_nombre_cliente`: Nombre del cliente (VARCHAR(255), default: NULL)
- `p_direccion`: Dirección del cliente (TEXT, default: NULL)
- `p_telefono_cliente`: Teléfono del cliente (VARCHAR(50), default: NULL)

### Parámetros Opcionales (Alternativos)
- `p_dispositivo_id_reparacion`: ID del dispositivo (BIGINT, default: NULL)
  - Si se proporciona, se usa este ID directamente en lugar de buscar por número de serie

## 🔄 Lógica del Procedimiento

1. **Validación de parámetros**: Verifica que los parámetros requeridos estén presentes
2. **Bloqueo de tablas**: Bloquea `clientes` y `dispositivos` para evitar condiciones de carrera
3. **Manejo de Cliente**:
   - Busca cliente por cédula
   - Si no existe y se proporciona `nombre_cliente`, crea uno nuevo
   - Si no existe y no se proporciona `nombre_cliente`, lanza error
4. **Manejo de Dispositivo**:
   - Si se proporciona `p_dispositivo_id_reparacion`, usa ese ID directamente
   - Si no, busca por `numero_serie`
   - Si no existe y se proporcionan `tipo` y `marca`, crea uno nuevo
   - Si existe, actualiza sus datos si se proporcionan nuevos valores
5. **Manejo de Reparación**:
   - Verifica si la reparación ya existe (por ID)
   - Si existe, actualiza los datos
   - Si no existe, inserta una nueva reparación

## 📝 Ejemplo de Uso en SQL

```sql
SELECT InsertarReparacionCompleta(
    1,                              -- p_id_reparacion
    'En proceso',                   -- p_estado
    50000.0,                        -- p_precio_reparacion
    'formateo del equipo',          -- p_descripcion
    '2023-12-01 00:00:00'::TIMESTAMP, -- p_fecha_entrega
    'SN123456',                     -- p_numero_serie
    'Celular',                      -- p_tipo
    'Samsung',                      -- p_marca
    'Galaxy S21',                   -- p_modelo
    'Pantalla rota',                -- p_reporte
    '2025-06-15 22:18:14'::TIMESTAMP, -- p_fecha_ingreso
    '123456789',                    -- p_cedula
    'Juan Pérez',                   -- p_nombre_cliente
    'Calle 123',                    -- p_direccion
    '555-1234'                      -- p_telefono_cliente
);
```

## 🔌 Uso desde Python (ORM)

El modelo `Reparaciones` ahora incluye el método `insertar_reparacion_completa()`:

```python
from api.app.models.reparaciones_model import Reparaciones

data = {
    "id_reparacion": 1,
    "estado": "En proceso",
    "precio_reparacion": 50000.0,
    "descripcion": "formateo del equipo",
    "fecha_entrega": "2023-12-01T00:00:00",
    "numero_serie": "SN123456",
    "tipo": "Celular",
    "marca": "Samsung",
    "modelo": "Galaxy S21",
    "reporte": "Pantalla rota",
    "fecha_ingreso": "2025-06-15T22:18:14.658067",
    "cedula": "123456789",
    "nombre_cliente": "Juan Pérez",
    "direccion": "Calle 123",
    "telefono_cliente": "555-1234"
}

success = Reparaciones.insertar_reparacion_completa(data)
if success:
    print("Reparación insertada exitosamente")
else:
    print("Error al insertar reparación")
```

## ⚠️ Manejo de Errores

El procedimiento puede lanzar las siguientes excepciones:

- `El ID de reparación es obligatorio`: Si `p_id_reparacion` es NULL
- `La cédula del cliente es obligatoria`: Si `p_cedula` es NULL
- `Debe proporcionarse número de serie o ID de dispositivo`: Si ambos son NULL
- `Para crear nuevo cliente se requiere nombre_cliente`: Si el cliente no existe y no se proporciona nombre
- `Para crear nuevo dispositivo se requiere tipo y marca`: Si el dispositivo no existe y faltan datos
- `Dispositivo con ID X no encontrado`: Si se proporciona un ID de dispositivo que no existe
- `Error: Ya existe un registro con estos datos`: Si hay violación de unicidad
- `Error: Referencia inválida`: Si hay violación de foreign key

## 🔄 Diferencias con el Procedimiento Anterior

### Antes (`insertar_reparacion_con_serie`)
- ❌ Solo manejaba reparación y dispositivo
- ❌ Requería que el dispositivo ya existiera
- ❌ No manejaba cliente
- ❌ No actualizaba datos del dispositivo

### Ahora (`InsertarReparacionCompleta`)
- ✅ Maneja cliente, dispositivo y reparación
- ✅ Crea automáticamente cliente y dispositivo si no existen
- ✅ Actualiza datos si el dispositivo existe
- ✅ Maneja transacciones completas
- ✅ Alineado con el ORM y JSON completo

## 📦 Instalación

Ejecuta el script SQL en tu base de datos PostgreSQL:

```bash
psql -U tu_usuario -d tu_base_de_datos -f postgresql/insertar_reparacion_completa.sql
```

O desde pgAdmin:
1. Abre pgAdmin
2. Conecta a tu base de datos
3. Abre Query Tool
4. Copia y pega el contenido de `insertar_reparacion_completa.sql`
5. Ejecuta el script

## 🧪 Testing

Para probar el procedimiento:

```sql
-- Caso 1: Cliente y dispositivo existen
SELECT InsertarReparacionCompleta(
    1, 'En proceso', 50000.0, 'Formateo', NOW()::TIMESTAMP,
    'SN123456', NULL, NULL, NULL, NULL, NULL,
    '123456789', NULL, NULL, NULL, NULL
);

-- Caso 2: Crear nuevo cliente y dispositivo
SELECT InsertarReparacionCompleta(
    2, 'Pendiente', 75000.0, 'Cambio de pantalla', NOW()::TIMESTAMP + INTERVAL '7 days',
    'SN789012', 'Celular', 'Apple', 'iPhone 14', 'Pantalla rota', NOW()::TIMESTAMP,
    '987654321', 'María García', 'Av. Principal 456', '555-5678', NULL
);

-- Caso 3: Usar dispositivo existente por ID
SELECT InsertarReparacionCompleta(
    3, 'Completada', 100000.0, 'Reparación completa', NOW()::TIMESTAMP,
    NULL, NULL, NULL, NULL, NULL, NULL,
    '123456789', NULL, NULL, NULL, 1  -- dispositivo_id_reparacion = 1
);
```

## 🎯 Beneficios

1. **Código más limpio**: Un solo procedimiento maneja toda la lógica
2. **Transaccional**: Garantiza consistencia de datos
3. **Flexible**: Acepta diferentes combinaciones de parámetros
4. **Robusto**: Validaciones y manejo de errores completo
5. **Alineado con ORM**: Usa los mismos nombres de campos que el modelo Python
