from flask import Blueprint
from .routers.cliente_routers import cliente_routes

api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

# ------------------------ Ruta Cliente --------------------------------------
api_v1.register_blueprint(cliente_routes)