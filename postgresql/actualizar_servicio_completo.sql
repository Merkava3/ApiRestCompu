-- Procedimiento almacenado para actualizar servicio completo
-- Corrige el problema de actualización de dirección en la tabla clientes
-- Los parámetros coinciden con los esperados por el código Python en const.py

CREATE OR REPLACE PROCEDURE actualizar_servicio_completo(
    p_id_servicio        bigint,
    p_nombre_cliente     text default null,
    p_cedula_cliente     text default null,
    p_direccion_cliente  text default null,
    p_telefono_cliente   text default null,
    p_tipo_dispositivo   text default null,
    p_marca_dispositivo  text default null,
    p_modelo_dispositivo text default null,
    p_reporte_dispositivo text default null,
    p_pago_servicio      float default null,
    p_precio_servicio    float default null
)
language plpgsql
as $$
declare
    v_cliente_id bigint;
    v_dispositivo_id bigint;
begin
    ------------------------------------------------------------------
    -- Obtener IDs necesarios
    ------------------------------------------------------------------
    select cliente_id_servicio, dispositivos_id_servicio
    into v_cliente_id, v_dispositivo_id
    from servicios
    where id_servicio = p_id_servicio;

    if not found then
        raise exception 'Servicio con id % no encontrado', p_id_servicio;
    end if;

    ------------------------------------------------------------------
    -- Actualizar SERVICIOS
    ------------------------------------------------------------------
    update servicios
    set
        pago = coalesce(p_pago_servicio, pago),
        precio_servicio = coalesce(p_precio_servicio, precio_servicio)
    where id_servicio = p_id_servicio;

    ------------------------------------------------------------------
    -- Actualizar CLIENTES
    -- CORREGIDO: Usa variables locales en lugar de FROM para evitar problemas
    -- Actualiza solo si el parámetro no es NULL
    ------------------------------------------------------------------
    if p_nombre_cliente is not null or p_direccion_cliente is not null or p_telefono_cliente is not null then
        update clientes
        set
            nombre_cliente  = coalesce(p_nombre_cliente, nombre_cliente),
            direccion       = coalesce(p_direccion_cliente, direccion),
            telefono_cliente = coalesce(p_telefono_cliente, telefono_cliente)
        where id_cliente = v_cliente_id;
        
        if not found then
            raise exception 'Cliente con id % no encontrado', v_cliente_id;
        end if;
    end if;

    ------------------------------------------------------------------
    -- Actualizar DISPOSITIVOS
    ------------------------------------------------------------------
    update dispositivos
    set
        marca = coalesce(p_marca_dispositivo, marca),
        modelo = coalesce(p_modelo_dispositivo, modelo),
        reporte = coalesce(p_reporte_dispositivo, reporte),
        tipo = coalesce(p_tipo_dispositivo, tipo)
    where id_dispositivo = v_dispositivo_id;
end;
$$;
