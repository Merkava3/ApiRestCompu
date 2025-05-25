# helpers/auth.py
from functools import wraps
from flask import request, jsonify
from ..models import Usuario
from ..helpers.response import unauthorized

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return unauthorized("Token de autenticación requerido")
        
        # Eliminar 'Bearer ' si está presente
        if token.startswith('Bearer '):
            token = token[7:]
        
        usuario = Usuario.check_token(token)
        if not usuario or not usuario.autenticado:
            return unauthorized("Token inválido o expirado")
            
        return f(usuario, *args, **kwargs)
    return decorated_function