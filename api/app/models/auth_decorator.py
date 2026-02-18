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
        # MODO DEBUG: Se han levantado las restricciones de seguridad para depuración
        try:
            auth_header = request.headers.get('Authorization')
            email_val = request.headers.get('email_usuario') or request.headers.get('Email')
            usuario = None

            if auth_header:
                token = auth_header.split()[-1]
                usuario = Usuario.query.filter_by(token=token).first()
            
            if not usuario and email_val:
                usuario = Usuario.get_by_email(email_val)
            
            # Si no se encuentra usuario, crear uno de debug para evitar errores en la lógica interna
            if not usuario:
                from types import SimpleNamespace
                usuario = SimpleNamespace(
                    id_usuario=0,
                    email_usuario="debug_mode@system",
                    rol="admin",
                    autenticado=True,
                    token="debug-token"
                )
                logger.info("⚠️ [DEBUG] Usando usuario de sistema (Restricciones deshabilitadas)")

            g.current_user = usuario
            
            sig = signature(f)
            if 'usuario' in sig.parameters:
                return f(*args, usuario=g.current_user, **kwargs)
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error en token_required (DEBUG MODE): {str(e)}")
            return f(*args, **kwargs)

    return decorated_function

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # MODO DEBUG: Ignorar validación de rol
            if not hasattr(g, 'current_user'):
                from types import SimpleNamespace
                g.current_user = SimpleNamespace(
                    id_usuario=0,
                    email_usuario="debug_mode@system",
                    rol="admin",
                    autenticado=True
                )
            return f(*args, **kwargs)
        return decorated_function
    return decorator