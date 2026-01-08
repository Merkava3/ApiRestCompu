-- Procedimiento almacenado para insertar reparación completa
-- Maneja cliente, dispositivo y reparación en una sola transacción
-- Alineado con el ORM y el JSON proporcionado

CREATE OR REPLACE FUNCTION InsertarReparacionCompleta(
    -- Reparación (requerido)
    p_id_reparacion BIGINT,
    p_estado VARCHAR(45),
    p_precio_reparacion DOUBLE PRECISION,
    p_descripcion TEXT,
    p_fecha_entrega TIMESTAMP,
    
    -- Dispositivo (buscar por número de serie o crear)
    p_numero_serie VARCHAR(255),
    p_tipo VARCHAR(255) DEFAULT NULL,
    p_marca VARCHAR(255) DEFAULT NULL,
    p_modelo VARCHAR(255) DEFAULT NULL,
    p_reporte TEXT DEFAULT NULL,
    p_fecha_ingreso TIMESTAMP DEFAULT NULL,
    
    -- Cliente (buscar por cédula o crear)
    p_cedula VARCHAR(16),
    p_nombre_cliente VARCHAR(255) DEFAULT NULL,
    p_direccion TEXT DEFAULT NULL,
    p_telefono_cliente VARCHAR(50) DEFAULT NULL,
    
    -- Opciones
    p_dispositivo_id_reparacion BIGINT DEFAULT NULL  -- Si se proporciona, usa este ID directamente
)
RETURNS BIGINT AS $$
DECLARE
    v_cliente_id BIGINT;
    v_dispositivo_id BIGINT;
    v_existing_reparacion BIGINT;
BEGIN
    ------------------------------------------------------------------
    -- Validación de parámetros requeridos
    ------------------------------------------------------------------
    IF p_id_reparacion IS NULL THEN
        RAISE EXCEPTION 'El ID de reparación es obligatorio';
    END IF;
    
    IF p_cedula IS NULL THEN
        RAISE EXCEPTION 'La cédula del cliente es obligatoria';
    END IF;
    
    IF p_numero_serie IS NULL AND p_dispositivo_id_reparacion IS NULL THEN
        RAISE EXCEPTION 'Debe proporcionarse número de serie o ID de dispositivo';
    END IF;
    
    ------------------------------------------------------------------
    -- Bloqueo para evitar inserción duplicada
    ------------------------------------------------------------------
    LOCK TABLE clientes IN EXCLUSIVE MODE;
    LOCK TABLE dispositivos IN EXCLUSIVE MODE;
    
    ------------------------------------------------------------------
    -- 1. Buscar o crear CLIENTE
    ------------------------------------------------------------------
    SELECT id_cliente INTO v_cliente_id
    FROM clientes
    WHERE cedula = p_cedula;
    
    IF v_cliente_id IS NULL THEN
        -- Crear nuevo cliente
        IF p_nombre_cliente IS NULL THEN
            RAISE EXCEPTION 'Para crear nuevo cliente se requiere nombre_cliente';
        END IF;
        
        INSERT INTO clientes (cedula, nombre_cliente, direccion, telefono_cliente)
        VALUES (
            p_cedula,
            p_nombre_cliente,
            COALESCE(p_direccion, 'No especificada'),
            COALESCE(p_telefono_cliente, 'No especificado')
        )
        RETURNING id_cliente INTO v_cliente_id;
        
        RAISE NOTICE 'Nuevo cliente creado: % (%)', p_nombre_cliente, p_cedula;
    END IF;
    
    ------------------------------------------------------------------
    -- 2. Buscar o crear DISPOSITIVO
    ------------------------------------------------------------------
    -- Si se proporciona dispositivo_id_reparacion, usarlo directamente
    IF p_dispositivo_id_reparacion IS NOT NULL THEN
        SELECT id_dispositivo INTO v_dispositivo_id
        FROM dispositivos
        WHERE id_dispositivo = p_dispositivo_id_reparacion;
        
        IF v_dispositivo_id IS NULL THEN
            RAISE EXCEPTION 'Dispositivo con ID % no encontrado', p_dispositivo_id_reparacion;
        END IF;
    ELSIF p_numero_serie IS NOT NULL THEN
        -- Buscar dispositivo por número de serie
        SELECT id_dispositivo INTO v_dispositivo_id
        FROM dispositivos
        WHERE numero_serie = p_numero_serie;
        
        IF v_dispositivo_id IS NULL THEN
            -- Crear nuevo dispositivo
            IF p_tipo IS NULL OR p_marca IS NULL THEN
                RAISE EXCEPTION 'Para crear nuevo dispositivo se requiere tipo y marca';
            END IF;
            
            INSERT INTO dispositivos (
                cliente_id_dispositivo,
                tipo,
                marca,
                modelo,
                reporte,
                numero_serie,
                fecha_ingreso
            ) VALUES (
                v_cliente_id,
                p_tipo,
                p_marca,
                COALESCE(p_modelo, 'No especificado'),
                COALESCE(p_reporte, 'Sin reporte'),
                p_numero_serie,
                COALESCE(p_fecha_ingreso, NOW())
            )
            RETURNING id_dispositivo INTO v_dispositivo_id;
            
            RAISE NOTICE 'Nuevo dispositivo creado: % - %', p_marca, p_numero_serie;
        ELSE
            -- Dispositivo existe, actualizar si se proporcionan nuevos datos
            IF p_tipo IS NOT NULL OR p_marca IS NOT NULL OR p_modelo IS NOT NULL OR p_reporte IS NOT NULL THEN
                UPDATE dispositivos
                SET
                    tipo = COALESCE(p_tipo, tipo),
                    marca = COALESCE(p_marca, marca),
                    modelo = COALESCE(p_modelo, modelo),
                    reporte = COALESCE(p_reporte, reporte)
                WHERE id_dispositivo = v_dispositivo_id;
            END IF;
        END IF;
    END IF;
    
    ------------------------------------------------------------------
    -- 3. Verificar si la reparación ya existe
    ------------------------------------------------------------------
    SELECT id_reparacion INTO v_existing_reparacion
    FROM reparaciones
    WHERE id_reparacion = p_id_reparacion;
    
    IF v_existing_reparacion IS NOT NULL THEN
        -- Actualizar reparación existente
        UPDATE reparaciones
        SET
            dispositivo_id_reparacion = v_dispositivo_id,
            estado = COALESCE(p_estado, estado),
            precio_reparacion = COALESCE(p_precio_reparacion, precio_reparacion),
            descripcion = COALESCE(p_descripcion, descripcion),
            fecha_entrega = COALESCE(p_fecha_entrega, fecha_entrega)
        WHERE id_reparacion = p_id_reparacion;
        
        RAISE NOTICE 'Reparación % actualizada', p_id_reparacion;
        RETURN p_id_reparacion;
    ELSE
        -- Insertar nueva reparación
        INSERT INTO reparaciones (
            id_reparacion,
            dispositivo_id_reparacion,
            estado,
            precio_reparacion,
            descripcion,
            fecha_entrega
        ) VALUES (
            p_id_reparacion,
            v_dispositivo_id,
            COALESCE(p_estado, 'Pendiente'),
            p_precio_reparacion,
            COALESCE(p_descripcion, 'Sin descripción'),
            COALESCE(p_fecha_entrega, NOW() + INTERVAL '7 days')
        );
        
        RAISE NOTICE 'Reparación % insertada exitosamente para dispositivo ID: %', p_id_reparacion, v_dispositivo_id;
        RETURN p_id_reparacion;
    END IF;
    
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Error: Ya existe un registro con estos datos (posible duplicado de ID de reparación)';
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Error: Referencia inválida (dispositivo o cliente no existe)';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error al insertar reparación completa: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Ejemplo de uso:
-- SELECT InsertarReparacionCompleta(
--     1,                              -- p_id_reparacion
--     'En proceso',                   -- p_estado
--     50000.0,                        -- p_precio_reparacion
--     'formateo del equipo',          -- p_descripcion
--     '2023-12-01 00:00:00'::TIMESTAMP, -- p_fecha_entrega
--     'SN123456',                     -- p_numero_serie
--     'Celular',                      -- p_tipo
--     'Samsung',                      -- p_marca
--     'Galaxy S21',                   -- p_modelo
--     'Pantalla rota',                -- p_reporte
--     '2025-06-15 22:18:14'::TIMESTAMP, -- p_fecha_ingreso
--     '123456789',                    -- p_cedula
--     'Juan Pérez',                   -- p_nombre_cliente
--     NULL,                           -- p_direccion (opcional)
--     NULL                            -- p_telefono_cliente (opcional)
-- );
