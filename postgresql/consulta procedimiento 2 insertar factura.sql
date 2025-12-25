select * from productos;
select * from compras;
select * from detalles_compras;
select * from usuarios;
select * from proveedores;

ALTER TABLE compras 
RENAME COLUMN id_compra TO id_compras;

ALTER TABLE compras 
ALTER COLUMN fecha_compras SET DEFAULT CURRENT_DATE;


CREATE OR REPLACE FUNCTION InsertarCompra(
    p_email_usuario VARCHAR(255),  -- Correo del usuario
    p_nit_proveedor VARCHAR(16),   -- NIT del proveedor
    p_nombre_proveedor VARCHAR(255), -- Nombre del proveedor
    p_info_contacto TEXT,          -- Información de contacto del proveedor
    p_metodo_pago VARCHAR(45),     -- Método de pago
    p_productos JSON               -- Lista de productos (formato JSON)
)
RETURNS VOID AS $$
DECLARE
    v_id_usuario BIGINT;
    v_id_proveedor BIGINT;
    v_id_compra BIGINT;
    v_total DECIMAL(10, 2) := 0;
    v_id_producto BIGINT;
    v_cantidad INT;
    v_precio DECIMAL(10, 2);
    v_subtotal DECIMAL(10, 2);
    v_product_count INT;
    v_product_json JSON;
BEGIN
    -- Obtener el ID del usuario a partir del correo
    SELECT id_usuario INTO v_id_usuario
    FROM usuarios
    WHERE email_usuario = p_email_usuario;

    -- Validar que el usuario exista
    IF v_id_usuario IS NULL THEN
        RAISE EXCEPTION 'Usuario no encontrado';
    END IF;

    -- Verificar si el proveedor ya existe por NIT
    SELECT id_proveedor INTO v_id_proveedor
    FROM proveedores
    WHERE nit = p_nit_proveedor;

    -- Si el proveedor no existe, se crea
    IF v_id_proveedor IS NULL THEN
        INSERT INTO proveedores (nit, nombre, informacion_contacto)
        VALUES (p_nit_proveedor, p_nombre_proveedor, p_info_contacto)
        RETURNING id_proveedor INTO v_id_proveedor;
    END IF;

    -- Insertar en la tabla compras
    INSERT INTO compras (total_compras, metodo_pago, id_proveedor_compras, id_usuario_compras)
    VALUES (0, p_metodo_pago, v_id_proveedor, v_id_usuario)
    RETURNING id_compras INTO v_id_compra;

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

        -- Insertar en la tabla detalles_compras
        INSERT INTO detalles_compras (cantidad, precio, id_compras_detalles, id_detalles_compras_productos)
        VALUES (v_cantidad, v_precio, v_id_compra, v_id_producto);

        -- Actualizar el total de la compra
        v_total := v_total + v_subtotal;
    END LOOP;

    -- Actualizar el total en la tabla compras
    UPDATE compras
    SET total_compras = v_total
    WHERE id_compras = v_id_compra;
END;
$$ LANGUAGE plpgsql;


SELECT InsertarCompra(
    'homero@gmail.com', 
    '754323-4', 
     'Proveedor Nuevo', 
	 'Dirección, Teléfono',
	 'Efectivo',
    '[{"id_producto": 48501, "cantidad": 2}]'::json
);

