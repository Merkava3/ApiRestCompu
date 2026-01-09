-- Procedimiento almacenado para insertar reparación completa
-- Maneja cliente, dispositivo y reparación en una sola transacción
-- Alineado con el ORM y el JSON proporcionado

CREATE OR REPLACE FUNCTION insertar_reparacion_completa(
    p_data JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_cliente_id BIGINT;
    v_dispositivo_id BIGINT;
    v_reparacion_id BIGINT;
BEGIN
    ------------------------------------------------------------------
    -- Validaciones mínimas
    ------------------------------------------------------------------
    IF p_data ->> 'cedula' IS NULL THEN
        RAISE EXCEPTION 'cedula es obligatoria';
    END IF;

    IF p_data ->> 'estado' IS NULL THEN
        RAISE EXCEPTION 'estado es obligatorio';
    END IF;

    IF p_data ->> 'precio_reparacion' IS NULL THEN
        RAISE EXCEPTION 'precio_reparacion es obligatorio';
    END IF;

    IF p_data ->> 'descripcion' IS NULL THEN
        RAISE EXCEPTION 'descripcion es obligatoria';
    END IF;

    ------------------------------------------------------------------
    -- 1. CLIENTE
    ------------------------------------------------------------------
    SELECT id_cliente
    INTO v_cliente_id
    FROM clientes
    WHERE cedula = p_data ->> 'cedula';

    IF v_cliente_id IS NULL THEN
        INSERT INTO clientes (
            cedula,
            nombre_cliente,
            direccion,
            telefono_cliente
        ) VALUES (
            p_data ->> 'cedula',
            p_data ->> 'nombre_cliente',
            COALESCE(p_data ->> 'direccion', 'No especificada'),
            COALESCE(p_data ->> 'telefono_cliente', 'No especificado')
        )
        RETURNING id_cliente INTO v_cliente_id;
    END IF;

    ------------------------------------------------------------------
    -- 2. DISPOSITIVO
    ------------------------------------------------------------------
    SELECT id_dispositivo
    INTO v_dispositivo_id
    FROM dispositivos
    WHERE numero_serie = p_data ->> 'numero_serie';

    IF v_dispositivo_id IS NULL THEN
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
            p_data ->> 'tipo',
            p_data ->> 'marca',
            p_data ->> 'modelo',
            p_data ->> 'reporte',
            p_data ->> 'numero_serie',
            COALESCE(
                (p_data ->> 'fecha_ingreso')::TIMESTAMP,
                NOW()
            )
        )
        RETURNING id_dispositivo INTO v_dispositivo_id;
    END IF;

    ------------------------------------------------------------------
    -- 3. REPARACIÓN (INSERT)
    ------------------------------------------------------------------
    v_reparacion_id := (p_data ->> 'id_reparacion')::BIGINT;

    INSERT INTO reparaciones (
        id_reparacion,
        dispositivo_id_reparacion,
        estado,
        precio_reparacion,
        descripcion
    ) VALUES (
        v_reparacion_id,
        v_dispositivo_id,
        p_data ->> 'estado',
        (p_data ->> 'precio_reparacion')::DOUBLE PRECISION,
        p_data ->> 'descripcion'
    );

    RETURN v_reparacion_id;
END;
$$;

-- Ejemplo de uso desde Python:
-- El id_reparacion se genera automáticamente en el endpoint
-- La fecha_entrega ya no es requerida
-- data = {
--     "estado": "En proceso",
--     "precio_reparacion": 50000.0,
--     "descripcion": "Formateo del equipo",
--     "numero_serie": "SN123456",
--     "tipo": "Celular",
--     "marca": "Samsung",
--     "modelo": "Galaxy S21",
--     "reporte": "Pantalla rota",
--     "fecha_ingreso": "2025-06-15 22:18:14",
--     "cedula": "123456789",
--     "nombre_cliente": "Juan Pérez",
--     "direccion": "Calle Principal 123",
--     "telefono_cliente": "+573001234567"
-- }
--
-- cursor.execute(
--     'SELECT insertar_reparacion_completa(%s::JSONB)',
--     (json.dumps(data),)
-- )
-- resultado = cursor.fetchone()[0]
