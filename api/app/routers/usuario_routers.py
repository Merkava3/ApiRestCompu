from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..models import Usuario
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *
from ..models.auth_decorator import token_required
from flask import g
from ..helpers.error_handler import handle_endpoint_errors, log_operation
from ..email.mailer import mailer

usuario_routes = Blueprint('usuarios_routes', __name__)

def set_usuarios_by():
    def decorator(function):
        def wrap(*args, **kwargs):
            json = request.get_json(force=True)
            id_usuario = json.get(ID_USUARIO)
            email_usuario = json.get(EMAIL_USUARIO)            
            
            usuario = None
            if id_usuario:
                usuario = Usuario.get_by_id(id_usuario)
            elif email_usuario:
                usuario = Usuario.get_by_email(email_usuario)
            
            if not usuario:
                return notFound()            
            return function(usuario, *args, **kwargs)
        wrap.__name__ = function.__name__
        return wrap
    return decorator

@usuario_routes.route('/usuarios', methods=['GET'])
@handle_endpoint_errors
def get_usuarios():
    # Obtiene lista de usuarios activos
    return successfully(api_usuarios.dump(Usuario.get_active_users()))

@usuario_routes.route('/usuario/register', methods=['POST'])
@handle_endpoint_errors
@log_operation("Registrar Usuario")
def post_user():
    # Registro de nuevo usuario con activacion por email
    json = request.get_json()
    if not json: return badRequest("Datos requeridos")

    # Validar campos obligatorios
    email = str(json.get(EMAIL_USUARIO, "")).strip().lower()
    if not email or not json.get("password") or not json.get("nombre_usuario"):
        return badRequest("Nombre, email y password son obligatorios")

    if Usuario.get_by_email(email):
        return badRequest("El email ya está registrado")

    # Carga basica de datos
    user = Usuario(
        nombre_usuario=str(json["nombre_usuario"]).strip(),
        email_usuario=email,
        rol=str(json.get("rol", "vendedor")).strip().lower(),
        autenticado=False,
        activo=False
    )
    user.set_password(str(json["password"]).strip())
    user.generate_auth_token() # Genera token para el enlace
    
    # Reset de estados iniciales
    user.autenticado = False
    user.ultima_autenticacion = None
    user.token_expiration = None

    if not user.save(): return serverError("Error al guardar")

    # Envio de correo de activacion
    activation_link = f"{request.url_root}api/v1/usuario/activate/{user.token}"
    mailer.send_email(
        "Bienvenido - Enlace de Acceso",
        f"Haz clic para activar: {activation_link}",
        user.email_usuario
    )

    return jsonify({
        "code": 201,
        "success": True,
        "message": "Usuario registrado. Revisa tu correo.",
        "data": {"usuario": {"nombre": user.nombre_usuario, "rol": user.rol}}
    }), 201

@usuario_routes.route('/usuario/activate/<token>', methods=['GET'])
@handle_endpoint_errors
def activate_user(token):
    # Activa usuario mediante el token del correo
    usuario = Usuario.query.filter_by(token=token).first()
    if not usuario: return notFound("Token inválido")

    usuario.autenticado = True
    usuario.ultima_autenticacion = datetime.utcnow()
    usuario.token_expiration = datetime.utcnow() # Dispara trigger DB
    
    if usuario.save():
        return successfully({
            "email_usuario": usuario.email_usuario,
            "autenticado": True
        })
    return badRequest("Error en activación")

@usuario_routes.route('/usuario', methods=['GET', 'DELETE'])
@set_usuarios_by()
def handle_usuario(usuario):
    # CRUD individual de usuario
    if request.method == 'GET':
        return successfully(api_usuario.dump(usuario))
    
    if request.method == 'DELETE':
        return delete() if usuario.delete() else badRequest()

@usuario_routes.route('/usuario/update', methods=['PUT'])
@set_usuarios_by()
def update_usuario(usuario):
    # Actualiza datos del usuario (nombres, email, password, rol)
    json = request.get_json(force=True)
    
    # Validar si el nuevo email ya está en uso por otro usuario
    if 'email_usuario' in json:
        nuevo_email = str(json['email_usuario']).strip().lower()
        if nuevo_email != usuario.email_usuario:
            usuario_existente = Usuario.get_by_email(nuevo_email)
            if usuario_existente:
                return badRequest("El email ya está registrado por otro usuario")
            usuario.email_usuario = nuevo_email

    # Mapeo según la consulta: update usuarios set nombres...
    if 'nombres' in json:
        usuario.nombre_usuario = json['nombres']
    if 'rol' in json:
        usuario.rol = json['rol']
    if 'password' in json:
        usuario.set_password(json['password'])
        
    # Guardar cambios
    if usuario.save():
        return update(api_usuario.dump(usuario))
    return badRequest("Error al actualizar usuario")

@usuario_routes.route('/usuario/login', methods=['POST'])
def login_usuario():
    # Login unificado: verifica si esta autenticado junto con el token internamente
    json = request.get_json(force=True)
    email = json.get(EMAIL_USUARIO)
    password = json.get("password")

    if not email or not password:
        return badRequest("Email y password requeridos")

    try:
        # Busca el usuario directamente para manejo interno
        user = Usuario.get_by_email(email)
        
        if not user:
            return unauthorized("Usuario no encontrado")

        # Verifica la contraseña usando el método del modelo
        if not Usuario.verify_password(user.password, password):
            return unauthorized("Contraseña incorrecta")

        # Genera el token (esto actualiza autenticado=True y ultima_autenticacion en el modelo)
        token = user.generate_auth_token()
        user.activo = True # Marca como activo el usuario en el sistema
        
        if user.save():
            return successfully({
                "email_usuario": user.email_usuario,
                "autenticado": user.autenticado,                
                "rol": user.rol
            })
        
        return serverError("Error al guardar estado de autenticación")
        
    except Exception as e:
        return serverError(str(e))

@usuario_routes.route('/usuario/logout', methods=['POST'])
def logout_usuario():
    # Logout solo actualiza activo a False
    email = request.get_json(force=True).get(EMAIL_USUARIO)
    if not email: return badRequest("Email requerido")

    try:
        user = Usuario.get_by_email(email)
        if user:
            user.activo = False
            if user.save():
                return successfully({"mensaje": "Sesión cerrada correctamente"})
        return badRequest("Usuario no encontrado")
    except Exception as e:
        return serverError(str(e))

@usuario_routes.route('/usuario/me', methods=['GET'])
@token_required
def get_current_user(usuario):
    # Retorna datos del usuario actual autenticado
    return successfully({"usuario": api_usuario.dump(usuario), "is_authenticated": True})

@usuario_routes.route('/renovar-token', methods=['POST'])
@token_required
def renovar_token():
    # Genera nuevo token para sesion activa
    usuario = g.current_user
    usuario.generate_auth_token()
    return successfully({"token": usuario.token}) if usuario.save() else badRequest()
