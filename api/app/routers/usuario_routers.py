from flask import Blueprint, request
from datetime import datetime
from ..models import Usuario
from ..helpers.response import *
from ..database.schemas import *
from ..helpers.helpers import Help
from ..helpers.const import *

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

    # Verificar si el usuario ya existe
    usuario_exist = Usuario.get_user(json.get(EMAIL_USUARIO))
    if usuario_exist:
        return badEquals()

    # Validar que la contraseña esté presente
    password = json.get("password")
    if not password:
        return badRequest("El campo 'password' es obligatorio")

    # Crear usuario sin incluir la contraseña en el constructor
    user = Usuario.new(
        nombre_usuario=json.get("nombre_usuario"),
        email_usuario=json.get("email_usuario")
    )

    # Encriptar la contraseña antes de guardarla
    user.set_password(password)

    # Generar ID si es necesario
    user = Help.generator_id(user, ID_USUARIO)

    # Guardar el usuario en la base de datos
    if user.save():
        return response(api_usuario.dump(user))
    return badRequest()

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

    email_usuario = json.get("email_usuario")  # Corrige el nombre del campo
    password = json.get("password")

    if not email_usuario or not password:
        return badRequest("Email y contraseña son obligatorios")

    usuario = Usuario.get_user(email_usuario)
    if not usuario:
        return unauthorized("Correo o contraseña incorrectos")

    if not usuario.check_password(password):
        return unauthorized("Correo o contraseña incorrectos")

    return successfully({
        "mensaje": "Inicio de sesión exitoso",
        "usuario": api_usuario.dump(usuario)
    })