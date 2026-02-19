from functools import wraps
from flask import g
from inspect import signature
from types import SimpleNamespace
import logging

# Configurar logging
logger = logging.getLogger(__name__)

def token_required(f):
    """
    Versión LIBRE del decorador.
    No valida nada, siempre permite el acceso e inyecta un usuario admin de sistema.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # MODO LIBRE: Seguridad totalmente deshabilitada
        # Siempre creamos un usuario de debug con rol admin para que nada falle aguas abajo
        g.current_user = SimpleNamespace(
            id_usuario=0,
            email_usuario="libre_acceso@system",
            rol="admin",
            autenticado=True,
            token="libre-token-debug"
        )
        
        # Inyectar el usuario si la función lo espera como argumento
        sig = signature(f)
        if 'usuario' in sig.parameters:
            return f(*args, usuario=g.current_user, **kwargs)
        
        return f(*args, **kwargs)

    return decorated_function

def role_required(role_name):
    """
    Versión LIBRE del decorador de roles.
    Ignora cualquier validación de rol.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Asegurar que g.current_user exista
            if not hasattr(g, 'current_user') or g.current_user is None:
                g.current_user = SimpleNamespace(
                    id_usuario=0,
                    email_usuario="libre_acceso@system",
                    rol="admin",
                    autenticado=True
                )
            return f(*args, **kwargs)
        return decorated_function
    return decorator