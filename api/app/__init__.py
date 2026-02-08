"""
Módulo de inicialización de la API.
Aplica el patrón Factory y delega la configuración modular a AppSetup.
"""
from typing import Type
from flask import Flask
from api.config import Config, get_config
from .helpers.app_setup import AppSetup


def create_app(environment: Type[Config] = None):
    """
    Crea y configura la instancia de la aplicación Flask.
    """
    if environment is None:
        environment = get_config()

    app = Flask(__name__)
    app.config.from_object(environment)

    # Inicialización modular delegada
    AppSetup.configure_cors(app)
    AppSetup.register_blueprints(app)
    AppSetup.init_database(app)
    AppSetup.init_cache(app)
    AppSetup.init_websockets(app)

    return app
