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
    try:
        json = request.get_json(force=True)
        if not json:
            return badRequest("Datos JSON requeridos")

        # Validación de tipos y conversión segura a strings
        nombre = str(json.get("nombre_usuario", "")).strip()
        email = str(json.get("email_usuario", "")).strip()
        password = str(json.get("password", "")).strip()

        # Validar campos obligatorios
        if not all([nombre, email, password]):
            return badRequest("Todos los campos son obligatorios y deben ser texto válido")

        # Verificar si el usuario ya existe
        if Usuario.get_user(email):
            return badEquals()

        # Crear nuevo usuario con los datos ya validados
        user = Usuario.new(
            nombre_usuario=nombre,
            email_usuario=email
        )
        
        # Validar y establecer contraseña
        if not isinstance(password, str) or len(password) < 4:
            return badRequest("La contraseña debe ser texto con al menos 4 caracteres")
        user.set_password(password)

        # Generar ID (asegurando que sea válido)
        user = Help.generator_id(user, ID_USUARIO)
        if not user.id_usuario:
            return badRequest("Error generando ID de usuario")

        # Generar token con validación adicional
        try:
            token = user.generate_auth_token()
            if not isinstance(token, str):
                raise ValueError("El token generado no es válido")
        except Exception as token_error:
            return serverError(f"Error generando token: {str(token_error)}")

        # Guardar usuario con validación
        if user.save():
            # Asegurar que api_usuario.dump() devuelve datos válidos
            usuario_data = api_usuario.dump(user)
            if not usuario_data:
                return serverError("Error serializando datos del usuario")

            return successfully({
                "code": 201,
                "success": True,
                "message": "Usuario registrado exitosamente",
                "data": {
                    "token": token,
                    "expires_in": 3600,
                    "token_type": "Bearer",
                    "usuario": usuario_data
                }
            }, 201)
        
        return badRequest("Error al guardar el usuario en la base de datos")
        
    except Exception as e:
        # Log del error completo para debugging
        print(f"Error completo en registro: {str(e)}")
        return serverError(f"Error en el servidor: Verifica los datos e intenta nuevamente")


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