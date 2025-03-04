from flask import jsonify

def badRequest():
    return jsonify({
        'sucess': False,
        'data': {},
        'mensaje': 'Falta un registro',
        'code': 400
        
    }), 400
    
def notFound():
    return jsonify({
        'sucess': False,
        'data': {},
        'mensaje': 'Dato no se encuentra',
        'code': 404
        }), 404

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
    
def successfully(data):
    return jsonify({
        'sucess': True,
        'data': data,
        'code': 200        
    }), 200
    
def update(data):
    return jsonify({
        'sucess': True,        
        'message': 'Registro Actualizado',        
        'code': 200        
    }), 200