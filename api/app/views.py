from flask import Blueprint
from .routers.cliente_routers import cliente_routes
from .routers.dispositivo_routers import dispositivo_routes

api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

# ------------------------ Ruta Cliente --------------------------------------
api_v1.register_blueprint(cliente_routes)

# ------------------------ Ruta Dispositivo ----------------------------------
api_v1.register_blueprint(dispositivo_routes)
