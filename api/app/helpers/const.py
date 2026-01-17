CAMPOS_CLIENTE = ('id_cliente', 'cedula', 'nombre_cliente', 'direccion', 'telefono_cliente')
CAMPOS_DISPOSITIVO = ('id_dispositivo', 'cliente_id_dispositivo', 'tipo', 'marca', 'modelo', 'reporte', 'numero_serie','fecha_ingreso')
CAMPOS_DISPOSITIVO_CON_CLIENTE = ("cedula", "nombre_cliente", "direccion", "telefono_cliente", "fecha_ingreso", "tipo", "modelo", "marca", "reporte", "numero_serie")
CAMPOS_REPARACIONES  = (
"id_reparacion",
    "dispositivo_id_reparacion",
    "cedula",
    "nombre_cliente",
    "precio_reparacion", 
    "tipo",
    "marca",
    "modelo",    
    "numero_serie",
    "reporte",
    "descripcion",
    "estado",
    "fecha_ingreso",
    "fecha_entrega"
)

CAMPOS_REPARACIONES_COMPLETAS = (
    "id_reparacion",
    "cedula",
    "nombre_cliente",
    "direccion",
    "telefono_cliente",
    "tipo",
    "marca",
    "modelo",
    "reporte",
    "numero_serie",
    "estado",
    "precio_reparacion",
    "descripcion",
    "fecha_entrega",
    "fecha_ingreso"
)

CAMPOS_USUARIO = ("id_usuario", "nombre_usuario", "email_usuario", "password", "autenticado", "ultima_autenticacion")
CAMPOS_SERVICIOS = ("estado","id_servicio","email_usuario","nombre_usuario","cedula", "nombre_cliente", "direccion", "telefono_cliente", "marca", "modelo", "reporte", "numero_serie", "fecha_ingreso", "fecha_servicio", "tipo_dispositivo", "tipo_servicio", "pago", "precio_servicio")
CAMPOS_SERVICIO_UPDATE = ("estado", "precio_servicio")


CAMPOS_PRODUCTOS = ("id_producto", "nombre_producto", "descripcion","precio", "stock")

CAMPOS_PROVEEDOR = ("id_proveedor", "nit", "nombre_proveedor", "informacion_contacto")

CAMPOS_INVENTARIO = ("id_inventario","id_producto", "nit", "nombre_proveedor", "nombre_producto", "precio", "stock", "cantidad", "ultima_actualizacion")

# --- variables de cliente ---
CEDULA_CLIENT = 'cedula'
ID_CLIENTE = 'id_cliente'

# --- variables de dispositivo ---
NUMERO_SERIE = 'numero_serie'
ID_DISPOSITIVO = 'id_dispositivo'

# --- variables de reparaciones ---
ID_REPARACION = 'id_reparacion'
DISPOSITIVO_ID_REPARACION = 'dispositivo_id_reparacion'

# --- variables de usuario ---
ID_USUARIO = 'id_usuario'
EMAIL_USUARIO = 'email_usuario'

# --- variables de servicios ---
ID_SERVICIO = 'id_servicio'

# --- variables de productos ---
ID_PRODUCTO = 'id_producto'

# --- variables de proveedor ---
ID_PROVEEDOR = 'id_proveedor'
NIT = 'nit'

# --- variables de inventario ---
ID_INVENTARIO = 'id_inventario'

# --- variables de facturas ---
ID_FACTURA = 'id_factura'

# --- variables de compras ---
ID_COMPRA = 'id_compra'

# --- procedimientos almacenados factura ---
INSERTAR_FACTURA = "SELECT InsertarFactura(:p_cedula, :p_pago, :p_id_usuario, :p_productos, :p_nombre_cliente, :p_direccion, :p_telefono_cliente)"
COLUMN_LIST_FACTURA = ["cedula", "pago", "id_usuario", "productos", "nombre_cliente", "direccion", "telefono_cliente"]

# --- procedimientos almacenados compra ---
INSERTAR_COMPRA = "SELECT InsertarCompra(:p_email_usuario, :p_nit, :p_nombre_proveedor, :p_informacion_contacto, :p_metodo_pago, :p_productos)"
COLUMN_LIST_COMPRA = ["email_usuario", "nit", "nombre_proveedor", "informacion_contacto", "metodo_pago", "productos"]

# --- procedimientos almacenados inventario ---
INSERTAR_INVENTARIO = "SELECT transferir_stock_json (:p_productos)"
COLUMN_LIST_INVENTARIO = ["productos"]

# --- procedimientos almacenados clientes dispositivo ---
INSERTAR_CLIENTE_DISPOSITIVO = "SELECT  InsertarClienteYDispositivo(:p_cedula, :p_nombre_cliente, :p_direccion, :p_telefono_cliente, :p_tipo, :p_marca, :p_modelo, :p_reporte, :p_numero_serie)"
COLUMN_LIST_CLIENTE_DISPOSITIVO = ["cedula", "nombre_cliente", "direccion", "telefono_cliente", "tipo", "marca", "modelo", "reporte", "numero_serie"]

# --- procedimientos almacenados servicio ---
INSERTAR_SERVICIO = """
    SELECT * FROM InsertarClienteYRelacionados(
        :p_id_servicio,
        :p_cedula_cliente,
        :p_nombre_cliente,
        :p_direccion_cliente,
        :p_telefono_cliente,
        :p_tipo_dispositivo,
        :p_marca_dispositivo,
        :p_modelo_dispositivo,
        :p_reporte_dispositivo,
        :p_numero_serie_dispositivo,
        :p_tipo_servicio,
        :p_descripcion_servicio,
        :p_fecha_servicio,
        :p_pago_servicio,
        :p_precio_servicio,
        :p_correo_usuario
    )
"""

columns_servicio_cliente = ["cedula", "dispositivo_id_reparacion", "estado", "fecha_entrega", "fecha_ingreso", "id_reparacion", "marca", "modelo", "nombre_cliente", "numero_serie", "precio_reparacion", "tipo"]	
   

COLUMN_LIST_SERVICIO = ["id_servicio", "cedula_cliente", "nombre_cliente", "direccion_cliente", "telefono_cliente", "tipo_dispositivo", "marca_dispositivo", "modelo_dispositivo", "reporte_dispositivo", "numero_serie_dispositivo", "tipo_servicio", "descripcion_servicio", "fecha_servicio", "pago_servicio", "precio_servicio", "correo_usuario"]

# --- procedimiento para actualizar servicio completo (actualizar_servicio_completo)
ACTUALIZAR_SERVICIO_COMPLETO = "CALL actualizar_servicio_completo_json(:p_id_servicio, CAST(:p_data AS jsonb))"
COLUMN_LIST_ACTUALIZAR_SERVICIO = ["id_servicio", "estado", "pago_servicio", "precio_servicio", "nombre_cliente", "direccion_cliente", "telefono_cliente", "tipo_dispositivo", "marca_dispositivo", "modelo_dispositivo", "reporte_dispositivo"]

CAMPOS_CONSULTA_SERVICIO = ("id_servicio", "cedula", "nombre_cliente", "telefono_cliente", "reporte", "tipo", "fecha_ingreso")

# --- procedimientos almacenados reparación ---
INSERTAR_REPARACION_COMPLETA = "SELECT insertar_reparacion_completa(CAST(:p_data AS jsonb))"

COLUMN_LIST_REPARACION_COMPLETA = [
    "id_reparacion",
    "estado",
    "precio_reparacion",
    "descripcion",
    "numero_serie",
    "tipo",
    "marca",
    "modelo",
    "reporte",
    "fecha_ingreso",
    "cedula",
    "nombre_cliente",
    "direccion",
    "telefono_cliente"
]

CAMPOS_BUSQUEDA = (ID_SERVICIO, ID_REPARACION, NUMERO_SERIE, CEDULA_CLIENT)

MAPEO_ATRIBUTOS_SERVICIO = {
    "email_usuario": "usuario.email_usuario",
    "nombre_usuario": "usuario.nombre_usuario",
    "cedula": "cliente.cedula",
    "nombre_cliente": "cliente.nombre_cliente",
    "direccion": "cliente.direccion",
    "telefono_cliente": "cliente.telefono_cliente",
    "marca": "dispositivos.marca",
    "modelo": "dispositivos.modelo",
    "reporte": "dispositivos.reporte",
    "numero_serie": "dispositivos.numero_serie",
    "tipo_dispositivo": "dispositivos.tipo",
    "tipo_servicio": "tipo",
    "fecha_ingreso": "dispositivos.fecha_ingreso",
    "fecha_servicio": "fecha_servicio"
}

# ---- const successful ----

SUCCESSFUL = {"mensaje": "Factura creada exitosamente"}
SUCCESSFULSERVICIO = {"mensaje": "Servicio actualizado exitosamente"}
SUCCESSFULREPARACION = {"mensaje": "Reparación creada exitosamente"}

# --- const error ----
ERROR = "Datos inválidos o faltantes"





