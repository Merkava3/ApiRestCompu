-- Procedimiento almacenado actualizado para aceptar id_servicio como parámetro
-- Ejecutar este script en PostgreSQL para actualizar el procedimiento almacenado

DROP FUNCTION IF EXISTS InsertarClienteYRelacionados(
    VARCHAR, VARCHAR, TEXT, VARCHAR, VARCHAR, VARCHAR, VARCHAR, TEXT, VARCHAR, 
    VARCHAR, TEXT, TIMESTAMP, DECIMAL, DECIMAL, TEXT
);

CREATE OR REPLACE FUNCTION InsertarClienteYRelacionados(
    p_id_servicio BIGINT,  -- NUEVO: primer parámetro para el ID del servicio
    p_cedula_cliente VARCHAR(16),
    p_nombre_cliente VARCHAR(255),
    p_direccion_cliente TEXT,
    p_telefono_cliente VARCHAR(50),
    p_tipo_dispositivo VARCHAR(255),
    p_marca_dispositivo VARCHAR(255),
    p_modelo_dispositivo VARCHAR(255),
    p_reporte_dispositivo TEXT,
    p_numero_serie_dispositivo VARCHAR(255),
    p_tipo_servicio VARCHAR(255),
    p_descripcion_servicio TEXT,
    p_fecha_servicio TIMESTAMP,
    p_pago_servicio DECIMAL(10, 2),
    p_precio_servicio DECIMAL(10, 2),
    p_correo_usuario TEXT
)
RETURNS BIGINT AS $$
DECLARE
    v_cliente_id BIGINT;
    v_usuario_id BIGINT;
    v_dispositivo_id BIGINT;
BEGIN
    -- Validación de parámetros obligatorios
    IF p_cedula_cliente IS NULL THEN
        RAISE EXCEPTION 'La cédula del cliente es obligatoria';
    END IF;
    
    IF p_nombre_cliente IS NULL THEN
        RAISE EXCEPTION 'El nombre del cliente es obligatorio';
    END IF;
    
    IF p_correo_usuario IS NULL THEN
        RAISE EXCEPTION 'El correo del usuario es obligatorio';
    END IF;

    -- Bloqueo para evitar inserción duplicada de clientes
    LOCK TABLE clientes IN EXCLUSIVE MODE;
    
    -- Buscar o insertar cliente
    SELECT id_cliente INTO v_cliente_id
    FROM clientes
    WHERE cedula = p_cedula_cliente;

    IF NOT FOUND THEN
        INSERT INTO clientes (cedula, nombre_cliente, direccion, telefono_cliente)
        VALUES (
            p_cedula_cliente, 
            p_nombre_cliente, 
            COALESCE(p_direccion_cliente, 'No especificada'), 
            COALESCE(p_telefono_cliente, 'No especificado')
        )
        RETURNING id_cliente INTO v_cliente_id;
    END IF;

    -- Validar y obtener usuario
    SELECT id_usuario INTO v_usuario_id
    FROM usuarios
    WHERE email_usuario = p_correo_usuario;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Usuario con correo % no encontrado', p_correo_usuario;
    END IF;

    -- Validar montos positivos (solo si no son NULL)
    IF (p_pago_servicio IS NOT NULL AND p_pago_servicio < 0) OR 
       (p_precio_servicio IS NOT NULL AND p_precio_servicio < 0) THEN
        RAISE EXCEPTION 'Los valores de pago y precio deben ser positivos';
    END IF;

    -- Insertar dispositivo con valores por defecto
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
        COALESCE(p_tipo_dispositivo, 'No especificado'),
        COALESCE(p_marca_dispositivo, 'No especificado'),
        COALESCE(p_modelo_dispositivo, 'No tiene registro'),
        COALESCE(p_reporte_dispositivo, 'Sin reporte'),
        COALESCE(p_numero_serie_dispositivo, 'No tiene registro'),
        NOW()
    ) RETURNING id_dispositivo INTO v_dispositivo_id;

    -- Insertar servicio con id_servicio personalizado (MODIFICADO)
    INSERT INTO servicios (
        id_servicio,  -- NUEVO: incluir id_servicio en el INSERT
        cliente_id_servicio, 
        dispositivos_id_servicio,
        usuario_id_servicio,
        tipo, 
        descripcion, 
        fecha_servicio, 
        pago, 
        precio_servicio,
        estado
    ) VALUES (
        p_id_servicio,  -- NUEVO: usar el id_servicio pasado como parámetro
        v_cliente_id, 
        v_dispositivo_id, 
        v_usuario_id, 
        COALESCE(p_tipo_servicio, 'General'),
        COALESCE(p_descripcion_servicio, 'Servicio estándar'),
        COALESCE(p_fecha_servicio, NOW()),
        COALESCE(p_pago_servicio, 0),  -- MODIFICADO: usar 0 si es NULL
        COALESCE(p_precio_servicio, 0),  -- MODIFICADO: usar 0 si es NULL
        'Pendiente' -- Estado por defecto
    );

    RETURN v_cliente_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Error: Ya existe un registro con estos datos (posible duplicado de cédula o número de serie)';
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Error: Referencia inválida (cliente o usuario no existe)';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error al insertar cliente y relacionados: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;
