"""
Módulo de configuración y configuración inicial de la aplicación (App Setup).
Aplica el principio de Responsabilidad Única (SRP) y encapsula la lógica de inicialización.
"""
from flask import Flask
from flask_cors import CORS
from .const import HEADERS, METHODS
from ..models import db
from ..views import api_v1
from ..cache import CacheMiddleware
from ..websocket_config import init_websocket

class AppSetup:
    """
    Clase encargada de orquestar la configuración de la instancia de Flask.
    """

    @staticmethod
    def configure_cors(app: Flask) -> None:
        """Configura el intercambio de recursos de origen cruzado (CORS)."""
        origins = app.config.get('CORS_ORIGINS')
        print(f"✅ [CORS] Configurando origenes: {origins}")
        
        # Headers adicionales comunes que podrian enviar los navegadores
        extended_headers = HEADERS + [
            'Cache-Control', 
            'Pragma', 
            'Expires', 
            'X-Requested-With', 
            'If-Modified-Since'
        ]
        
        CORS(
            app,
            resources={r"/api/*": {
                "origins": origins,
                "methods": METHODS,
                "allow_headers": extended_headers,
                "supports_credentials": True,
                "expose_headers": ["Content-Type", "Authorization"]
            }}
        )

    @staticmethod
    def register_blueprints(app: Flask) -> None:
        """Registra los Blueprints de la API."""
        if 'api_v1' not in app.blueprints:
            app.register_blueprint(api_v1, url_prefix='/api/v1')

    @staticmethod
    def init_database(app: Flask) -> None:
        """Inicializa la base de datos SQLAlchemy."""
        with app.app_context():
            db.init_app(app)
            if app.config.get('DEBUG') or app.config.get('TESTING'):
                db.create_all()

    @staticmethod
    def init_cache(app: Flask) -> None:
        """Inicializa el middleware de caché."""
        cache_middleware = CacheMiddleware()
        cache_middleware.init_app(app)

    @staticmethod
    def init_websockets(app: Flask) -> None:
        """Inicializa la funcionalidad de WebSockets para el chat."""
        try:
            websocket_initialized = init_websocket(app)
            if websocket_initialized:
                print("OK: WebSocket inicializado correctamente")
            else:
                print("WARN: WebSocket no pudo inicializarse - continuando sin chat")
        except Exception as ws_error:
            print(f"ERROR: Error critico inicializando WebSocket: {ws_error}")
            print("INFO: Servidor continuara sin funcionalidad de chat")
