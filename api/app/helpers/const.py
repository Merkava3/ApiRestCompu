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
    "estado",
    "fecha_ingreso",
    "fecha_entrega"
)

CAMPOS_USUARIO = ("id_usuario", "nombre_usuario", "email_usuario", "password", "autentificado", "ultima_autentificacion")
CAMPOS_SERVICIOS = ("estado","id_servicio","email_usuario","nombre_usuario","cedula", "nombre_cliente", "direccion", "telefono_cliente", "marca", "modelo", "reporte", "numero_serie", "fecha_ingreso", "fecha_servicio", "tipo_dispositivo", "tipo_servicio", "pago", "precio_servicio")

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

# ---- const successful ----

SUCCESSFUL = {"mensaje": "Factura creada exitosamente"}

# --- const error ----
ERROR = "Datos inválidos o faltantes"





