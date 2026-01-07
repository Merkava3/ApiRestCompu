"""
Punto de entrada principal de la aplicación.
"""
from api.app import create_app
from api.config import get_config


def create_application():
    """
    Factory function para crear la aplicación.
    Obtiene la configuración según la variable de entorno FLASK_ENV.
    """
    environment = get_config()
    return create_app(environment)


# Crear la aplicación
app = create_application()


if __name__ == "__main__":
    app.run(debug=app.config.get('DEBUG', False))
