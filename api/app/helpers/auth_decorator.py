from functools import wraps
from flask import request, g
from datetime import datetime
from ..models import Usuario
from ..helpers.response import unauthorized
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Obtener el token del header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return unauthorized("Token de autenticación requerido")

        # 2. Extraer el token (soporta 'Bearer token' o solo 'token')
        try:
            token = auth_header.split(' ')[1] if 'Bearer ' in auth_header else auth_header
        except IndexError:
            return unauthorized("Formato de token inválido")

        # 3. Verificar token en la base de datos
        usuario = Usuario.query.filter_by(token=token).first()
        if not usuario:
            return unauthorized("Token no encontrado")

        # 4. Verificar expiración
        if usuario.token_expiration < datetime.utcnow():
            return unauthorized("Token expirado")

        # 5. Verificar estado de autenticación
        if not usuario.autenticado:
            return unauthorized("Usuario no autenticado")

        # 6. Adjuntar usuario al contexto de Flask
        g.current_user = usuario

        # 7. Actualizar última actividad (opcional)
        usuario.ultima_autenticacion = datetime.utcnow()
        try:
            usuario.save()
        except Exception as e:
            print(f"Error actualizando última autenticación: {str(e)}")

        return f(*args, **kwargs)
    
    return decorated_function