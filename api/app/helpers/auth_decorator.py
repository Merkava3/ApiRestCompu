from functools import wraps
from flask import request
from ..models import Usuario
from ..helpers.response import unauthorized

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return unauthorized("Token de autenticación requerido")
        
        # Extraer el token (soporta 'Bearer' o token directo)
        token = auth_header.split(' ')[-1] if ' ' in auth_header else auth_header
        
        usuario = Usuario.check_token(token)
        if not usuario:
            return unauthorized("Token inválido o expirado")
            
        if not usuario.autenticado:
            return unauthorized("Usuario no autenticado")
            
        return f(usuario, *args, **kwargs)
    return decorated_function