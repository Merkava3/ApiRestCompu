from flask import Blueprint, jsonify
from .routers.cliente_routers import cliente_routes
from .routers.dispositivo_routers import dispositivo_routes
from .routers.usuario_routers import usuario_routes
from .routers.servicios_routers import servicios_routes
from .routers.producto_routers import productos_routes
from .routers.proveedor_routers import proveedor_routes
from .routers.inventario_routers import inventario_routes
from .routers.facturas_routers import facturas_routes
from .routers.chat_routers import chat_routes
from .routers.compras_routers import compras_routes
from .routers.dashboard_routers import dashboard_routes
from .websocket_config import check_websocket_health
api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

# ------------------------ Ruta Chat --------------------------------------
api_v1.register_blueprint(chat_routes)

# ======================== Health Check ====================================
@api_v1.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud del servidor."""
    return jsonify({"status": "ok", "message": "Servidor funcionando correctamente"}), 200

@api_v1.route('/health/websocket', methods=['GET'])
def websocket_health_check():
    """Endpoint de diagnóstico para WebSocket."""
    ws_status = check_websocket_health()
    status_code = 200 if ws_status.get("status") == "healthy" else 503
    return jsonify(ws_status), status_code

# ======================== Ruta Cliente ====================================
api_v1.register_blueprint(cliente_routes)

# ------------------------ Ruta Dispositivo ----------------------------------
api_v1.register_blueprint(dispositivo_routes)

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

# ------------------------ Ruta Dashboard ------------------------------------
api_v1.register_blueprint(dashboard_routes)
