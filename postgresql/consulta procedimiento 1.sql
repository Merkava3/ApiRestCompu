select * from clientes;
select * from usuarios;
select * from productos;
select * from facturas;

INSERT INTO facturas (id_cliente_facturas, total, pago, factura_id_usuario, fecha)
VALUES (v_id_cliente, 0, p_pago, p_id_usuario, NOW())
RETURNING id_factura;

SELECT column_name, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'facturas';

ALTER TABLE facturas 
ALTER COLUMN fecha SET DEFAULT CURRENT_TIMESTAMP;

drop procedure InsertarFactura;


SELECT
    p.proname AS procedure_name
FROM
    pg_proc p
JOIN
    pg_depend d ON p.oid = d.objid
JOIN
    pg_class c ON d.refobjid = c.oid
WHERE
    d.refclassid = 'pg_class'::regclass AND
    c.relname = 'facturas' -- Reemplaza con el nombre de tu tabla
AND
    d.deptype = 'i' -- 'i' significa internal dependency (e.g., trigger calling a function)
AND
    p.prokind = 'p'; -- 'p' indica que es un procedimiento

	SELECT
    p.proname AS procedure_name,
    pg_get_functiondef(p.oid) AS procedure_definition
FROM
    pg_proc p
LEFT JOIN
    pg_namespace n ON p.pronamespace = n.oid
WHERE
    n.nspname = 'public' -- Cambia 'public' al esquema donde está el procedimiento
    AND p.proname = 'InsertarFactura';

CREATE OR REPLACE FUNCTION InsertarFactura(
    p_cedula_cliente VARCHAR(20),  -- Cédula del cliente
    p_pago DECIMAL(10, 2),         -- Pago realizado
    p_id_usuario BIGINT,           -- ID del usuario
    p_productos JSON               -- Lista de productos (formato JSON)
)
RETURNS VOID AS $$
DECLARE
    v_id_factura INT;
    v_total DECIMAL(10, 2) := 0;
    v_id_cliente BIGINT;
    v_id_producto BIGINT;
    v_cantidad INT;
    v_precio DECIMAL(10, 2);
    v_subtotal DECIMAL(10, 2);
    v_product_count INT;
    v_product_json JSON;
BEGIN
    -- Obtener el ID del cliente a partir de la cédula
    SELECT id_cliente INTO v_id_cliente
    FROM clientes
    WHERE cedula = p_cedula_cliente;

    -- Validar que el cliente exista
    IF v_id_cliente IS NULL THEN
        RAISE EXCEPTION 'Cliente no encontrado';
    END IF;

    -- Insertar la factura con el pago inicial
    INSERT INTO facturas (id_cliente_facturas, total, pago, factura_id_usuario)
    VALUES (v_id_cliente, 0, p_pago, p_id_usuario)
    RETURNING id_factura INTO v_id_factura;

    -- Procesar los productos del JSON
    v_product_count := json_array_length(p_productos);
    
    FOR i IN 0..v_product_count-1 LOOP
        -- Extraer el producto actual
        v_product_json := p_productos->i;
        v_id_producto := (v_product_json->>'id_producto')::BIGINT;
        v_cantidad := (v_product_json->>'cantidad')::INT;

        -- Obtener el precio del producto
        SELECT precio INTO v_precio
        FROM productos
        WHERE id_producto = v_id_producto;

        -- Calcular el subtotal
        v_subtotal := v_precio * v_cantidad;

        -- Insertar el detalle de la factura
        INSERT INTO detalle_factura (factura_id_detalle, producto_id_detalle, cantidad_detalle, subtotal)
        VALUES (v_id_factura, v_id_producto, v_cantidad, v_subtotal);

        -- Actualizar el stock del producto
        UPDATE productos
        SET cantidad_stock = cantidad_stock - v_cantidad
        WHERE id_producto = v_id_producto;

        -- Actualizar el total de la factura
        v_total := v_total + v_subtotal;
    END LOOP;

    -- Actualizar el total de la factura
    UPDATE facturas
    SET total = v_total
    WHERE id_factura = v_id_factura;
END;
$$ LANGUAGE plpgsql;