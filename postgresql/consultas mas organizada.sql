CREATE OR REPLACE FUNCTION InsertarClienteYDispositivo(
    p_cedula VARCHAR(16),
    p_nombre_cliente VARCHAR(255),
    p_direccion TEXT,
    p_telefono_cliente VARCHAR(50),
    p_tipo VARCHAR(255),
    p_marca VARCHAR(255),
    p_modelo VARCHAR(255),
    p_reporte TEXT,
    p_numero_serie VARCHAR(255)
)
RETURNS BIGINT AS $$
DECLARE
    v_cliente_id BIGINT;
    v_existente_cliente RECORD;
    v_existente_dispositivo RECORD;
BEGIN
    -- Verificar si el cliente ya existe por su cédula
    SELECT id_cliente INTO v_existente_cliente
    FROM clientes
    WHERE cedula = p_cedula;

    IF FOUND THEN
        v_cliente_id := v_existente_cliente.id_cliente;
    ELSE
        -- Insertar nuevo cliente si no existe
        INSERT INTO clientes (cedula, nombre_cliente, direccion, telefono_cliente)
        VALUES (p_cedula, p_nombre_cliente, p_direccion, p_telefono_cliente)
        RETURNING id_cliente INTO v_cliente_id;
    END IF;

    -- Verificar si ya existe el dispositivo por su número de serie
    SELECT 1 INTO v_existente_dispositivo
    FROM dispositivos
    WHERE numero_serie = p_numero_serie;

    IF NOT FOUND THEN
        -- Insertar dispositivo si no existe
        INSERT INTO dispositivos (cliente_id_dispositivo, tipo, marca, modelo, reporte, numero_serie)
        VALUES (v_cliente_id, p_tipo, p_marca, p_modelo, p_reporte, p_numero_serie);
    END IF;

    RETURN v_cliente_id;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error al insertar cliente y dispositivo: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE dispositivos
ALTER COLUMN fecha_ingreso SET DEFAULT NOW();


SELECT * FROM InsertarClienteYDispositivo(
    '55677',
    'Juan Pérez',
    'Calle 123, Bogotá',
    '3123456789',
    'Teléfono',
    'Samsung',
    'Galaxy S21',
    'Pantalla dañada',
    'SN145678903'
);


select * from clientes;
select * from dispositivos;

---------------------------------------------------------------------------------------------------------------------


CREATE OR REPLACE FUNCTION InsertarClienteYRelacionados(
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

    -- Validar montos positivos
    IF p_pago_servicio < 0 OR p_precio_servicio < 0 THEN
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

    -- Insertar servicio con nombres de columnas exactos
    INSERT INTO servicios (
        cliente_id_servicio, 
        dispositivos_id_servicio,  -- Nombre exacto de la columna
        usuario_id_servicio,       -- Nombre exacto de la columna
        tipo, 
        descripcion, 
        fecha_servicio, 
        pago, 
        precio_servicio,
        estado
    ) VALUES (
        v_cliente_id, 
        v_dispositivo_id, 
        v_usuario_id, 
        COALESCE(p_tipo_servicio, 'General'),
        COALESCE(p_descripcion_servicio, 'Servicio estándar'),
        COALESCE(p_fecha_servicio, NOW()),
        p_pago_servicio, 
        p_precio_servicio,
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


SELECT * FROM InsertarClienteYRelacionados(
    p_cedula_cliente => '123456789'::VARCHAR(16),
    p_nombre_cliente => 'Juan Pérez'::VARCHAR(255),
    p_direccion_cliente => 'Calle 123, Bogotá'::TEXT,
    p_telefono_cliente => '3123456789'::VARCHAR(50),
    p_tipo_dispositivo => 'Celular'::VARCHAR(255),
    p_marca_dispositivo => 'Samsung'::VARCHAR(255),
    p_modelo_dispositivo => 'Galaxy S21'::VARCHAR(255),
    p_reporte_dispositivo => 'Pantalla rota'::TEXT,
    p_numero_serie_dispositivo => 'SN123456'::VARCHAR(255),
    p_tipo_servicio => 'Reparación'::VARCHAR(255),
    p_descripcion_servicio => 'Cambio de pantalla'::TEXT,
    p_fecha_servicio => NOW()::TIMESTAMP,
    p_pago_servicio => 50000.00::DECIMAL(10,2),
    p_precio_servicio => 120000.00::DECIMAL(10,2),
    p_correo_usuario => 'homero@mail.com'::TEXT
);

select * from usuarios;
