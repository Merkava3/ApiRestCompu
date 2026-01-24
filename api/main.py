"""
Punto de entrada principal de la aplicación con soporte para Socket.IO.
"""
import eventlet
# Monkey patch must be the very first thing
eventlet.monkey_patch()

from api.app import create_app, socketio
from api.config import get_config
import os


def create_application():
    """
    Factory function para crear la aplicación.
    Obtiene la configuración según la variable de entorno FLASK_ENV.
    """
    environment = get_config()
    return create_app(environment)


# Crear la aplicación Flask
app = create_application()


if __name__ == "__main__":
    # Iniciar servidor con soporte para Socket.IO
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        debug=app.config.get('DEBUG', False)
    )
