"""
Factory function para crear y configurar la aplicación Flask.
Aplica el patrón Factory para la inicialización de la app.
Integra caché automático para optimizar rendimiento.
"""
from flask import Flask
from flask_cors import CORS
from typing import Type

from .models import db
from .views import api_v1
from .cache import CacheMiddleware
from api.config import Config, get_config
from .helpers.const import METHODS, HEADERS
from flask_socketio import SocketIO
from .routers.chat_routers import register_chat_handlers

# Instancia global de SocketIO
socketio = SocketIO()


def create_app(environment: Type[Config] = None):
    """
    Factory function para crear la aplicación Flask.
    
    Args:
        environment: Clase de configuración. Si es None, usa get_config()
    
    Returns:
        Flask app configurada con caché integrado
    """
    if environment is None:
        environment = get_config()
    
    app = Flask(__name__)
    app.config.from_object(environment)
    
    # Configurar CORS
    CORS(
        app,
        origins=app.config.get('CORS_ORIGINS', ['*']),
        methods=METHODS,
        allow_headers=HEADERS,
        supports_credentials=True,
        max_age=3600
    )
    
    # Registrar blueprints
    if 'api_v1' not in app.blueprints:
        app.register_blueprint(api_v1, url_prefix='/api/v1')
    
    # Inicializar base de datos
    with app.app_context():
        db.init_app(app)
        # Solo crear tablas en desarrollo/testing
        if app.config.get('DEBUG') or app.config.get('TESTING'):
            db.create_all()
    
    # Inicializar middleware de caché
    cache_middleware = CacheMiddleware()
    cache_middleware.init_app(app)
    
    # Inicializar SocketIO
    socketio.init_app(app, cors_allowed_origins="*")

    # Registrar manejadores de chat
    register_chat_handlers(socketio)
    
    return app