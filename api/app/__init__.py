"""
Factory function para crear y configurar la aplicación Flask.
Aplica el patrón Factory para la inicialización de la app.
"""
from flask import Flask
from flask_cors import CORS
from typing import Type

from .models import db
from .views import api_v1
from api.config import Config, get_config


def create_app(environment: Type[Config] = None):
    """
    Factory function para crear la aplicación Flask.
    
    Args:
        environment: Clase de configuración. Si es None, usa get_config()
    
    Returns:
        Flask app configurada
    """
    if environment is None:
        environment = get_config()
    
    app = Flask(__name__)
    app.config.from_object(environment)
    
    # Configurar CORS
    CORS(
        app, 
        resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}},
        supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True)
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
    
    return app