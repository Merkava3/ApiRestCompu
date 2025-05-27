from flask import Blueprint, request
from datetime import datetime
from ..models import Usuario
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..helpers.auth_decorator import token_required
from flask import g

usuario_routes = Blueprint('usuarios_routes', __name__)

def set_usuarios_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_usuario = json.get(ID_USUARIO)
            email_usuario = json.get(EMAIL_USUARIO)            
            # Buscar primero por ID, luego por Número de Serie o Cédula
            if email_usuario:
                usuario = Usuario.get_user(email_usuario) 
            if id_usuario:
                usuario = Usuario.get_user_id(id_usuario)         
            if not usuario:
                return notFound()            
            return function(usuario, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@usuario_routes.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuario = Usuario.query.all()
    return successfully(api_usuarios.dump(usuario))

@usuario_routes.route('/usuario', methods=['POST'])
def post_user():
    json = request.get_json(force=True)

    # Validaciones existentes...
    usuario_exist = Usuario.get_user(json.get(EMAIL_USUARIO))
    if usuario_exist:
        return badEquals()

    required_fields = ["nombre_usuario", "email_usuario", "password"]
    for field in required_fields:
        if not json.get(field):
            return badRequest(f"El campo '{field}' es obligatorio")

    try:
        user = Usuario.new(
            nombre_usuario=json.get("nombre_usuario"),
            email_usuario=json.get("email_usuario")
        )
        user.set_password(json.get("password"))
        user = Help.generator_id(user, ID_USUARIO)
        
        # Generar token SOLO durante el registro
        token = user.generate_auth_token()
        
        if user.save():
            return successfully({
                "mensaje": "Usuario registrado exitosamente",
                "token": token,  # Token generado durante registro
                "expires_in": 3600,
                "token_type": "Bearer",
                "usuario": api_usuario.dump(user)
            }, 201)
        return badRequest("Error al guardar el usuario")
    except Exception as e:
        return serverError(f"Error en el servidor: {str(e)}")


@usuario_routes.route('/usuario', methods=['GET'])
@set_usuarios_by()
def get_usuario(usuario):  
    return successfully(api_usuario.dump(usuario))

@usuario_routes.route('/usuario', methods=['DELETE'])
@set_usuarios_by()
def delete_usuario(usuario):
    if usuario.delete():
        return delete()
    return badRequest()

@usuario_routes.route('/usuario', methods=['PUT'])
@set_usuarios_by()
def put_usuario(usuario):
    json = request.get_json(force=True)
    for key, value in json.items():
        setattr(usuario, key, value)
    if usuario.save():
        return update(api_usuario.dump(usuario))      
    return badRequest()

@usuario_routes.route('/usuario/auth', methods=['PUT'])
@set_usuarios_by()
def auth_usuario(usuario):
    usuario.autenticado = True
    usuario.ultima_autenticacion = datetime.utcnow()
    if usuario.save():
        return update(api_usuario.dump(usuario))      
    return badRequest()

@usuario_routes.route('/usuario/login', methods=['POST'])
def login_usuario():
    json = request.get_json(force=True)
    
    if not json:
        return badRequest("Datos de autenticación requeridos")

    email = json.get("email_usuario")
    password = json.get("password")

    if not email or not password:
        return badRequest("Email y contraseña son obligatorios")

    usuario = Usuario.get_user(email)
    if not usuario:
        return unauthorized("Credenciales incorrectas")

    if not usuario.check_password(password):
        return unauthorized("Credenciales incorrectas")

    try:
        # Verificar si el usuario tiene un token válido
        if not usuario.token or not usuario.token_expiration or usuario.token_expiration < datetime.utcnow():
            return unauthorized("No hay token válido. Contacte al administrador")
        
        # Actualizar última autenticación SIN generar nuevo token
        usuario.ultima_autenticacion = datetime.utcnow()
        usuario.autenticado = True
        
        if usuario.save():
            return successfully({
                "mensaje": "Inicio de sesión exitoso",
                "token": usuario.token,  # Usa el token existente
                "expires_in": (usuario.token_expiration - datetime.utcnow()).total_seconds(),
                "token_type": "Bearer",
                "usuario": api_usuario.dump(usuario)
            })
        return badRequest("Error al actualizar la autenticación")
    except Exception as e:
        return serverError(f"Error en el servidor: {str(e)}")

@usuario_routes.route('/usuario/logout', methods=['POST'])
@token_required
def logout_usuario(usuario):
    """Endpoint para cerrar sesión"""
    usuario.revoke_token()
    if usuario.save():
        return successfully({"mensaje": "Sesión cerrada correctamente"})
    return badRequest("Error al cerrar sesión")

@usuario_routes.route('/usuario/me', methods=['GET'])
@token_required
def get_current_user(usuario):
    """Endpoint protegido que devuelve datos del usuario actual"""
    return successfully({
        "usuario": api_usuario.dump(usuario),
        "is_authenticated": usuario.autenticado
    })

@usuario_routes.route('/renovar-token', methods=['POST'])
@token_required
def renovar_token():
    usuario = g.current_user
    nuevo_token = usuario.generate_auth_token()
    if usuario.save():
        return successfully({"token": nuevo_token})
    return badRequest("Error al renovar token")