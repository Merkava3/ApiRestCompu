from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .usuario_model import Usuario
from .cliente_model import Cliente