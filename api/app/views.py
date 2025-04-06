from flask import Blueprint
from .routers.cliente_routers import cliente_routes
from .routers.dispositivo_routers import dispositivo_routes
from .routers.reparacion_routers import reparacion_routes
from .routers.usuario_routers import usuario_routes
from .routers.servicios_routers import servicios_routes
from .routers.producto_routers import productos_routes
from .routers.proveedor_routers import proveedor_routes
from .routers.inventario_routers import inventario_routes
from .routers.facturas_routeres import facturas_routes
from .routers.compras_routers import compras_routes
api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

# ------------------------ Ruta Cliente --------------------------------------
api_v1.register_blueprint(cliente_routes)

# ------------------------ Ruta Dispositivo ----------------------------------
api_v1.register_blueprint(dispositivo_routes)

# ------------------------ Ruta Reparaciones ---------------------------------
api_v1.register_blueprint(reparacion_routes)

# ------------------------ Ruta Servicios ------------------------------------
api_v1.register_blueprint(servicios_routes)

# ------------------------ Ruta Usuario --------------------------------------
api_v1.register_blueprint(usuario_routes)

# ------------------------ Ruta Producto -------------------------------------
api_v1.register_blueprint(productos_routes)

# ------------------------ Ruta Proveedor ------------------------------------
api_v1.register_blueprint(proveedor_routes)

# ------------------------ Ruta Inventario -----------------------------------
api_v1.register_blueprint(inventario_routes)

# ------------------------ Ruta Facturas -------------------------------------
api_v1.register_blueprint(facturas_routes)

# ------------------------ Ruta Compras --------------------------------------
api_v1.register_blueprint(compras_routes)