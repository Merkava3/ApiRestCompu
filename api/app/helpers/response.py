"""
Módulo de utilidades para respuestas HTTP estandarizadas.
Proporciona funciones consistentes para generar respuestas JSON.
"""
from flask import jsonify
from typing import Any, Optional, Dict


class ResponseHelper:
    """
    Clase helper para generar respuestas HTTP estandarizadas.
    Mantiene consistencia en la estructura de respuestas.
    """
    
    @staticmethod
    def success(data: Any = None, message: str = "Operación exitosa", 
                status_code: int = 200) -> tuple:
        """
        Genera una respuesta exitosa.
        
        Args:
            data: Datos a incluir en la respuesta
            message: Mensaje descriptivo
            status_code: Código HTTP (default: 200)
        
        Returns:
            tuple: (jsonify response, status_code)
        """
        response = {
            "success": True,
            "code": status_code,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: str = "Error en la operación", 
              status_code: int = 400, 
              details: Optional[Dict[str, Any]] = None) -> tuple:
        """
        Genera una respuesta de error.
        
        Args:
            message: Mensaje de error
            status_code: Código HTTP (default: 400)
            details: Detalles adicionales del error
        
        Returns:
            tuple: (jsonify response, status_code)
        """
        response = {
            "success": False,
            "code": status_code,
            "message": message
        }
        if details:
            response["details"] = details
        return jsonify(response), status_code
    
    @staticmethod
    def created(data: Any = None, message: str = "Registrado exitosamente") -> tuple:
        """Genera una respuesta de creación exitosa (201)."""
        return ResponseHelper.success(data, message, 201)
    
    @staticmethod
    def not_found(message: str = "Recurso no encontrado") -> tuple:
        """Genera una respuesta 404."""
        return ResponseHelper.error(message, 404)
    
    @staticmethod
    def unauthorized(message: str = "No autorizado") -> tuple:
        """Genera una respuesta 401."""
        return ResponseHelper.error(message, 401)
    
    @staticmethod
    def bad_request(message: str = "Solicitud incorrecta") -> tuple:
        """Genera una respuesta 400."""
        return ResponseHelper.error(message, 400)
    
    @staticmethod
    def conflict(message: str = "Conflicto: recurso ya existe") -> tuple:
        """Genera una respuesta 409."""
        return ResponseHelper.error(message, 409)
    
    @staticmethod
    def server_error(message: str = "Error interno del servidor") -> tuple:
        """Genera una respuesta 500."""
        return ResponseHelper.error(message, 500)


# Funciones de compatibilidad con el código existente
# Estas mantienen la misma interfaz pero usan ResponseHelper internamente
def response(data: Any) -> tuple:
    """Compatibilidad: Genera respuesta exitosa con formato legacy."""
    return jsonify({
        'success': True,
        'message': "Registrado Exitosamente",
        'data': data
    }), 200


def successfully(data: Optional[Any] = None, message: str = "Operación exitosa", 
                 status_code: int = 200) -> tuple:
    """Compatibilidad: Genera respuesta exitosa."""
    return ResponseHelper.success(data, message, status_code)


def badRequest(message: str = "Solicitud incorrecta") -> tuple:
    """Compatibilidad: Genera respuesta 400."""
    return ResponseHelper.bad_request(message)


def notFound(message: str = "Recurso no encontrado") -> tuple:
    """Compatibilidad: Genera respuesta 404 con formato legacy."""
    return jsonify({
        'success': False,
        'data': {},
        'message': message,
        'code': 404
    }), 404


def unauthorized(message: str = "No autorizado") -> tuple:
    """Compatibilidad: Genera respuesta 401."""
    return ResponseHelper.unauthorized(message)


def badEquals(message: str = "Registro ya existente") -> tuple:
    """Compatibilidad: Genera respuesta 409 con formato legacy."""
    return jsonify({
        'success': False,
        'data': {},
        "message": message,
        "code": 409
    }), 409


def delete() -> tuple:
    """Compatibilidad: Genera respuesta de eliminación exitosa."""
    return jsonify({
        'success': True,
        'data': {},
        'message': 'Registro eliminado',
        'code': 200
    }), 200


def update(data: Optional[Any] = None) -> tuple:
    """Compatibilidad: Genera respuesta de actualización exitosa."""
    response = {
        'success': True,
        'message': 'Registro Actualizado',
        'code': 200
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), 200


def serverError(message: str = "Error interno del servidor") -> tuple:
    """Compatibilidad: Genera respuesta 500."""
    return ResponseHelper.server_error(message)
