"""
Constantes y enumerables para la API REST Compu.
Sigue el esquema PostgreSQL → SQLAlchemy types.
"""

# ======================== ENUMERABLES ========================
# Roles de usuario
ROLES_USUARIO = ('admin', 'tecnico', 'vendedor')

# Estados de servicios
ESTADOS_SERVICIO = ('recibido', "revision",'en_proceso', 'instalando' ,'finalizado', 'entregado')

# Métodos de pago
METODOS_PAGO = ('efectivo', 'tarjeta', 'transferencia', 'credito')

# ======================== CAMPOS DE TABLAS ========================
CAMPOS_CLIENTE = ('id_cliente', 'cedula', 'nombre_cliente', 'direccion', 'telefono_cliente', 'created_at', 'updated_at', 'activo')
CAMPOS_DISPOSITIVO = ('id_dispositivo', 'cliente_id_dispositivo', 'tipo', 'marca', 'modelo', 'numero_serie', 'descripcion', 'fecha_ingreso', 'created_at', 'updated_at', 'activo')
CAMPOS_DISPOSITIVO_CON_CLIENTE = ("cedula", "nombre_cliente", "direccion", "telefono_cliente", "fecha_ingreso", "tipo", "modelo", "marca", "numero_serie", "descripcion")

CAMPOS_USUARIO = ("id_usuario", "nombre_usuario", "email_usuario", "password", "rol", "autenticado", "ultima_autenticacion", "token", "created_at", "updated_at", "activo")

CAMPOS_SERVICIOS = ("id_servicio", "cliente_id_servicio", "dispositivo_id_servicio", "usuario_id_servicio", "tipo_servicio", "fecha_servicio", "precio_servicio", "descripcion", "estado_servicio", "fecha_entrega", "created_at", "updated_at", "activo")
CAMPOS_SERVICIO_UPDATE = ("estado_servicio", "precio_servicio", "fecha_entrega")
CAMPOS_SERVICIOS_COMPLETOS = ("id_servicio", "cedula", "nombre_cliente", "direccion", "telefono_cliente", "tipo_servicio", "descripcion","marca", "modelo", "tipo", "numero_serie", "estado_servicio", "reporte", "fecha_ingreso", "fecha_entrega", "dias", "precio_servicio", "email_usuario")
CAMPOS_SERVICIOS_CEDULA = ("id_servicio", "cedula", "nombre_cliente", "direccion", "telefono_cliente", "marca", "tipo", "estado_servicio", "fecha_ingreso", "precio_servicio", "email_usuario")

CAMPOS_PRODUCTOS = ("id_producto", "nombre_producto", "descripcion", "precio_venta", "cantidad_stock", "created_at", "updated_at", "activo")

CAMPOS_PROVEEDOR = ("id_proveedor", "nit", "nombre", "informacion_contacto", "created_at", "updated_at", "activo")

CAMPOS_INVENTARIO = ("id_inventario", "id_producto", "nit", "nombre_proveedor", "nombre_producto", "precio_venta", "cantidad_stock", "ultima_actualizacion")

CAMPOS_FACTURAS = ("id_factura", "cliente_id_factura", "usuario_id_factura", "fecha", "pago", "total", "created_at", "updated_at", "activo")

CAMPOS_DETALLE_FACTURA = ("id_detalle", "factura_id_detalle", "producto_id_detalle", "cantidad_detalle", "subtotal")

CAMPOS_COMPRAS = ("id_compras", "proveedor_id_compras", "usuario_id_compras", "fecha_compras", "total_compras", "metodo_pago", "created_at", "updated_at", "activo")

CAMPOS_DETALLE_COMPRA = ("id_detalles_compras", "compras_id_detalles", "producto_id_detalles", "cantidad", "precio")

# ======================== IDENTIFICADORES DE CAMPO ========================
CEDULA_CLIENT = 'cedula'
ID_CLIENTE = 'id_cliente'
NUMERO_SERIE = 'numero_serie'
ID_DISPOSITIVO = 'id_dispositivo'
ID_USUARIO = 'id_usuario'
EMAIL_USUARIO = 'email_usuario'
ID_SERVICIO = 'id_servicio'
ID_PRODUCTO = 'id_producto'
ID_PROVEEDOR = 'id_proveedor'
NIT = 'nit'
ID_INVENTARIO = 'id_inventario'
ID_FACTURA = 'id_factura'
ID_COMPRA = 'id_compra'
ID_DETALLES_COMPRA = 'id_detalles_compras'
ID_DETALLE_FACTURA = 'id_detalle'
CLIENTE_ID_DISPOSITIVO = 'cliente_id_dispositivo'
CLIENTE_ID_SERVICIO = 'cliente_id_servicio'
DISPOSITIVO_ID_SERVICIO = 'dispositivo_id_servicio'
USUARIO_ID_SERVICIO = 'usuario_id_servicio'
USUARIO_ID_FACTURA = 'usuario_id_factura'
CLIENTE_ID_FACTURA = 'cliente_id_factura'
USUARIO_ID_COMPRA = 'usuario_id_compras'
PROVEEDOR_ID_COMPRA = 'proveedor_id_compras'
PRODUCTO_ID_DETALLE = 'producto_id_detalle'
FACTURA_ID_DETALLE = 'factura_id_detalle'
PRODUCTO_ID_DETALLES = 'producto_id_detalles'
COMPRAS_ID_DETALLES = 'compras_id_detalles'

# ======================== MENSAJES DE RESPUESTA ========================
SUCCESSFUL = {"mensaje": "Operación exitosa"}
SUCCESSFULCLIENTE = {"mensaje": "Cliente creado exitosamente"}
SUCCESSFULDEVICE = {"mensaje": "Dispositivo creado exitosamente"}
SUCCESSFULSERVICIO = {"mensaje": "Servicio actualizado exitosamente"}
SUCCESSFULFACTURA = {"mensaje": "Factura creada exitosamente"}
SUCCESSFULCOMPRA = {"mensaje": "Compra creada exitosamente"}
SUCCESSFULINVENTARIO = {"mensaje": "Inventario actualizado exitosamente"}

ERROR = "Datos inválidos o faltantes"
ERROR_NO_ENCONTRADO = "El registro no fue encontrado"
ERROR_DUPLICADO = "El registro ya existe"

# ======================== CONSULTAS SQL ========================
INSERTAR_SERVICIO_JSON = "CALL sp_guardar_servicio_json(:p_data)"

CAMPOS_SERVICIO_JSON = (
    "id_servicio",
    "usuario_email",
    "cedula",
    "nombre_cliente",
    "direccion",
    "telefono_cliente",
    "numero_serie",
    "tipo",
    "marca",
    "modelo",
    "reporte",
    "tipo_servicio",
    "precio_servicio",
    "descripcion",
    "estado_servicio"
)
COLUMN_LIST_ACTUALIZAR_SERVICIO = CAMPOS_SERVICIO_JSON
ACTUALIZAR_SERVICIO_JSON = "CALL sp_actualizar_servicio_json(:p_data)"

# ======================== MAPEOS DE ATRIBUTOS ========================
MAPEO_ATRIBUTOS_SERVICIO = {
    "email_usuario": "usuario.email_usuario",
    "nombre_usuario": "usuario.nombre_usuario",
    "cedula": "cliente.cedula",
    "nombre_cliente": "cliente.nombre_cliente",
    "direccion": "cliente.direccion",
    "telefono_cliente": "cliente.telefono_cliente",
    "marca": "dispositivo.marca",
    "modelo": "dispositivo.modelo",
    "numero_serie": "dispositivo.numero_serie",
    "tipo_dispositivo": "dispositivo.tipo",
    "tipo_servicio": "tipo_servicio",
    "fecha_ingreso": "dispositivo.fecha_ingreso",
    "fecha_servicio": "fecha_servicio"
}

FIELD_MAPPING = {
    'direccion': 'direccion_cliente',
    'marca': 'marca_dispositivo',
    'modelo': 'modelo_dispositivo',
    'numero_serie': 'numero_serie_dispositivo',
    'pago': 'pago_servicio',
    'precio': 'precio_servicio',
    'tipo': 'tipo_dispositivo',
    'cedula': 'cedula_cliente'
}









