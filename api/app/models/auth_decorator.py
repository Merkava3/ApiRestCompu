from functools import wraps
from flask import request, g
from datetime import datetime
from . import Usuario
from . import db
from inspect import signature
from ..helpers.response import unauthorized
import logging

# Configurar logging
logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # MODO LIBRE: Seguridad totalmente deshabilitada
        try:
            # Siempre creamos un usuario de debug con rol admin para que nada falle
            from types import SimpleNamespace
            usuario = SimpleNamespace(
                id_usuario=0,
                email_usuario="libre_acceso@system",
                rol="admin",
                autenticado=True,
                token="libre-token-debug"
            )
            g.current_user = usuario
            
            sig = signature(f)
            if 'usuario' in sig.parameters:
                return f(*args, usuario=g.current_user, **kwargs)
            return f(*args, **kwargs)
        except Exception as e:
            return f(*args, **kwargs)

    return decorated_function

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # MODO LIBRE: Ignorar validación de rol
            if not hasattr(g, 'current_user'):
                from types import SimpleNamespace
                g.current_user = SimpleNamespace(
                    id_usuario=0,
                    email_usuario="libre_acceso@system",
                    rol="admin",
                    autenticado=True
                )
            return f(*args, **kwargs)
        return decorated_function
    return decorator