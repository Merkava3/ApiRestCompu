from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import Usuario
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..models.auth_decorator import token_required
from flask import g
from ..helpers.error_handler import handle_endpoint_errors, log_operation

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
@handle_endpoint_errors
def get_usuarios():
    usuario = Usuario.query.all()
    return successfully(api_usuarios.dump(usuario))

@usuario_routes.route('/usuario', methods=['POST'])
@handle_endpoint_errors
@log_operation("Registrar Usuario")
def post_user():
    json = request.get_json()
    if not json:
        return badRequest("Datos JSON requeridos")

    # Validación de campos
    required_fields = {
        "nombre_usuario": "Nombre de usuario es requerido",
        "email_usuario": "Email es requerido",
        "password": "Contraseña es requerida"
    }
    
    missing_fields = [field for field, msg in required_fields.items() if not json.get(field)]
    if missing_fields:
        return badRequest(", ".join([required_fields[field] for field in missing_fields]))

    # Normalización y limpieza
    nombre = str(json["nombre_usuario"]).strip()
    email = str(json["email_usuario"]).strip().lower()
    password = str(json["password"]).strip()

    # Verificar si el usuario ya existe
    if Usuario.get_user(email):
        return badRequest("El email ya está registrado")

    # Validar contraseña
    if len(password) < 8:
        return badRequest("La contraseña debe tener al menos 8 caracteres")

    # Crear nuevo usuario
    user = Usuario(
        nombre_usuario=nombre,
        email_usuario=email
    )
    user.set_password(password)

    # Generar ID (si es necesario, según tu implementación)
    if hasattr(Help, 'generator_id'):
        user = Help.generator_id(user, ID_USUARIO)

    # Generar token JWT (esto actualiza user.token y user.token_expiration automáticamente)
    token = user.generate_auth_token()
    if not isinstance(token, str):
        return serverError("Formato de token inválido")

    # Guardar usando el método save() existente
    if not user.save():
        return serverError("Error al guardar el usuario en la base de datos")

    # Serializar datos del usuario
    usuario_data = api_usuario.dump(user)
    if not usuario_data:
        return serverError("Error serializando datos del usuario")

    # Respuesta exitosa
    return jsonify({
        "code": 201,
        "success": True,
        "message": "Usuario registrado exitosamente",
        "data": {
            "token": token,
            "expires_in": 3600,
            "token_type": "Bearer",
            "usuario": usuario_data
        }
    }), 201

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

# validation 
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