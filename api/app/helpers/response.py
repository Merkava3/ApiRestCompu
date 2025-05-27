from flask import jsonify

def badRequest(message="Solicitud incorrecta"):
    return jsonify({
        "code": 400,
        "success": False,
        "message": message
    }), 400

def notFound():
    return jsonify({
        'sucess': False,
        'data': {},
        'mensaje': 'Dato no se encuentra',
        'code': 404
        }), 404

def unauthorized(message="No autorizado"):
    return jsonify({
        "status": "error",
        "message": message
    }), 401

def badEquals():
    return jsonify({
        'sucess': False,
        'data': {},
        "message": "Registro ya existente",
        "code": 404
    }), 404
      
def response(data):   
    return jsonify(
        {
            'sucess': True,
           'message': "Registrado Exitosamente",
            'data':  data
        }      
    ), 200

def delete():
    return jsonify({        
        'sucess': True,
        'data': {},
        'message': 'Registro eliminado',
        'code': 200
    }), 200
    
def successfully(data=None, message="Operación exitosa", status_code=200):
    response = {
        "code": status_code,
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code
    
def update(data):
    return jsonify({
        'sucess': True,        
        'message': 'Registro Actualizado',        
        'code': 200        
    }), 200

def serverError(message="Error interno del servidor"):
    return jsonify({
        "code": 500,
        "success": False,
        "message": message
    }), 500