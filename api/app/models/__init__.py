"""
Inicialización de modelos SQLAlchemy.
Importa todos los modelos de la aplicación.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importación de modelos
from .usuario_model import Usuario
from .cliente_model import Cliente
from .dispositivo_model import Dispositivo
from .servicio_model import Servicios
# Importación de modelos
from .usuario_model import Usuario
from .cliente_model import Cliente
from .dispositivo_model import Dispositivo
from .servicio_model import Servicios

__all__ = [
    'db',
    'Usuario',
    'Cliente',
    'Dispositivo',
    'Servicios'
]
