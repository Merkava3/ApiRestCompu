SELECT pg_get_functiondef(oid)
FROM pg_proc
WHERE proname = 'insertarfactura';

DROP FUNCTION IF EXISTS public.insertarfactura(
    character varying,  -- p_cedula_cliente
    numeric,           -- p_pago
    bigint,            -- p_id_usuario
    json              -- p_productos
);


CREATE OR REPLACE FUNCTION InsertarFactura(
    p_cedula_cliente VARCHAR(20),  -- Cédula del cliente
    p_pago DECIMAL(10, 2),         -- Pago realizado
    p_id_usuario BIGINT,           -- ID del usuario
    p_productos JSON               -- Lista de productos (formato JSON)
)
RETURNS VOID AS $$
DECLARE
    v_id_factura BIGINT;
    v_total DECIMAL(10, 2) := 0;
    v_id_cliente BIGINT;
    v_id_producto BIGINT;
    v_cantidad INT;
    v_precio DECIMAL(10, 2);
    v_subtotal DECIMAL(10, 2);
    v_product_count INT;
    v_product_json JSON;
    v_stock INT;
BEGIN
    -- Obtener el ID del cliente a partir de la cédula
    SELECT id_cliente INTO v_id_cliente
    FROM clientes
    WHERE cedula = p_cedula_cliente;

    -- Validar que el cliente exista
    IF v_id_cliente IS NULL THEN
        RAISE EXCEPTION 'Cliente no encontrado';
    END IF;

    -- Insertar la factura con la fecha actual
    INSERT INTO facturas (id_cliente_facturas, total, pago, factura_id_usuario, fecha)
    VALUES (v_id_cliente, 0, p_pago, p_id_usuario, NOW())
    RETURNING id_factura INTO v_id_factura;

    -- Procesar los productos del JSON
    v_product_count := json_array_length(p_productos);
    
    FOR i IN 0..v_product_count-1 LOOP
        -- Extraer el producto actual
        v_product_json := p_productos->i;
        v_id_producto := (v_product_json->>'id_producto')::BIGINT;
        v_cantidad := (v_product_json->>'cantidad')::INT;

        -- Obtener el precio y stock del producto
        SELECT precio, stock INTO v_precio, v_stock
        FROM productos
        WHERE id_producto = v_id_producto;

        -- Validar que el producto exista
        IF v_precio IS NULL THEN
            RAISE EXCEPTION 'Producto con ID % no encontrado', v_id_producto;
        END IF;

        -- Verificar que haya stock suficiente
        IF v_stock < v_cantidad THEN
            RAISE EXCEPTION 'Stock insuficiente para el producto ID %', v_id_producto;
        END IF;

        -- Calcular el subtotal
        v_subtotal := v_precio * v_cantidad;

        -- Insertar el detalle de la factura
        INSERT INTO detalle_factura (factura_id_factura, producto_id_producto, cantidad_detalle, sub_total)
        VALUES (v_id_factura, v_id_producto, v_cantidad, v_subtotal);

        -- Actualizar el stock del producto
        UPDATE productos
        SET stock = stock - v_cantidad
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