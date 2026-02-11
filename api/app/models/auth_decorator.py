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
        try:
            # El usuario indica que el frontend no envía token, sino que se identifica por correo
            # Intentamos obtener la identidad de varias formas:
            auth_header = request.headers.get('Authorization')
            email_val = request.headers.get('email_usuario') or request.headers.get('Email')
            
            usuario = None

            # 1. Intentar por Token si existe el header Authorization
            if auth_header:
                token = auth_header.split()[-1]
                usuario = Usuario.query.filter_by(token=token).first()
                if usuario:
                    # Validar expiración si es por token
                    if usuario.token_expiration and usuario.token_expiration < datetime.utcnow():
                        logger.warning(f"Token expirado para usuario {usuario.email_usuario}")
                        return unauthorized("Sesión expirada, por favor inicie sesión de nuevo")

            # 2. Intentar por Email (si no se encontró por token o no se envió)
            if not usuario and email_val:
                usuario = Usuario.get_by_email(email_val)
            
            # 3. Buscar en el cuerpo del JSON o parámetros de consulta (Fallback)
            if not usuario:
                email_from_request = None
                if request.is_json:
                    try:
                        data = request.get_json(silent=True)
                        if data:
                            email_from_request = data.get('email_usuario') or data.get('email')
                    except:
                        pass
                
                if not email_from_request:
                    email_from_request = request.args.get('email_usuario') or request.args.get('email')
                
                if email_from_request:
                    usuario = Usuario.get_by_email(email_from_request)

            # Si no encontramos al usuario después de todos los intentos
            if not usuario:
                logger.warning("No se pudo identificar al usuario (sin token ni email)")
                return unauthorized("Identificación requerida (Token o Email)")

            # Verificación que pide el usuario: "debe estar autenticado el true"
            if not usuario.autenticado:
                logger.warning(f"Usuario {usuario.email_usuario} encontrado pero no está autenticado (autenticado=false)")
                return unauthorized("Usuario no autenticado")

            # Adjuntar usuario al contexto para que role_required pueda usarlo
            g.current_user = usuario
            logger.debug(f"Acceso permitido para: {usuario.email_usuario}")

            # Se valida si la funcion decorada acepta el argumento usuario
            sig = signature(f)
            func_params = sig.parameters

            if 'usuario' in func_params:
                return f(*args, usuario=g.current_user, **kwargs)
            else:
                return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error inesperado en token_required: {str(e)}", exc_info=True)
            return unauthorized("Error validando autenticación")

    return decorated_function

def role_required(role_name):
    """
    Decorador para restringir acceso por rol. 
    Debe usarse después de @token_required
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return unauthorized("Error de sistema: Usuario no cargado para validar rol")
            
            if g.current_user.rol != role_name:
                logger.warning(f"Acceso denegado: Usuario {g.current_user.email_usuario} con rol {g.current_user.rol} intentó acceder a recurso de {role_name}")
                return unauthorized(f"Acceso denegado: Se requiere rol {role_name}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator