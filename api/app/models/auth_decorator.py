from functools import wraps
from flask import request, g
from datetime import datetime
from . import Usuario
from . import db
from ..helpers.response import unauthorized
import logging

# Configurar logging
logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 1. Obtener y validar el header Authorization
            auth_header = request.headers.get('Authorization')
            logger.debug(f"Header Authorization recibido: {auth_header}")
            
            if not auth_header:
                logger.warning("No se encontró header Authorization")
                return unauthorized("Token de autenticación requerido")

            # 2. Extraer el token de manera segura
            token_parts = auth_header.split()
            if len(token_parts) == 2 and token_parts[0].lower() == 'bearer':
                token = token_parts[1]
            elif len(token_parts) == 1:
                token = token_parts[0]
            else:
                logger.warning(f"Formato de token inválido: {auth_header}")
                return unauthorized("Formato de token inválido. Use: Bearer <token> o <token>")

            logger.debug(f"Token extraído: {token[:10]}...")  # Log parcial por seguridad

            # 3. Buscar usuario con token válido
            usuario = Usuario.query.filter_by(token=token).first()
            if not usuario:
                logger.warning("Token no encontrado en base de datos")
                return unauthorized("Token no válido")

            # 4. Verificar expiración
            if usuario.token_expiration < datetime.utcnow():
                logger.warning(f"Token expirado para usuario {usuario.id_usuario}")
                return unauthorized("Token expirado")

            # 5. Verificar estado de autenticación
            if not usuario.autenticado:
                logger.warning(f"Usuario {usuario.id_usuario} no está autenticado")
                return unauthorized("Usuario no autenticado")

            # 6. Adjuntar usuario al contexto
            g.current_user = usuario
            logger.debug(f"Usuario autenticado: {usuario.email_usuario}")

            # 7. Actualizar última actividad (sin bloquear la respuesta si falla)
            try:
                usuario.ultima_autenticacion = datetime.utcnow()
                db.session.commit()
                logger.debug("Última autenticación actualizada")
            except Exception as db_error:
                db.session.rollback()
                logger.error(f"Error actualizando última autenticación: {str(db_error)}")
                # No retornamos error, solo lo registramos

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error inesperado en token_required: {str(e)}", exc_info=True)
            return unauthorized("Error validando autenticación")

    return decorated_function