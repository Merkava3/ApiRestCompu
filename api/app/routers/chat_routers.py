"""
Rutas de API para gestión del chat.
"""
from flask import Blueprint, jsonify

from ..helpers.helpers import Help
from ..helpers.websocket_services import WebSocketConnectionManager
from ..websocket_config import check_websocket_health
from ..models.auth_decorator import token_required

chat_routes = Blueprint('chat_routes', __name__)
ws_manager = WebSocketConnectionManager()


@chat_routes.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Retorna todas las sesiones de chat."""
    history = Help.get_chat_history() or []
    unique_users = {}

    for msg in history:
        tel = msg['telefono']
        if tel == 'soporte_tecnico':
            continue
        unique_users[tel] = {
            "sid": tel,
            "nombres": msg['nombres'],
            "telefono": tel,
            "chat": msg['chat'],
            "id_anonimo": msg['id_anonimo']
        }

    # Connections active
    for user_id, info in ws_manager.get_all_connections().items():
        if user_id == 'soporte_tecnico' or user_id in unique_users:
            continue
        unique_users[user_id] = {
            "sid": user_id,
            "nombres": info.get('name', 'Usuario'),
            "telefono": info.get('phone', 'N/A'),
            "chat": "",
            "id_anonimo": user_id
        }

    return jsonify(list(unique_users.values())), 200


@chat_routes.route('/chat/history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """Retorna el historial de chat para un usuario."""
    return jsonify(Help.get_chat_history(user_id) or []), 200


@chat_routes.route('/chat/history/<user_id>', methods=['DELETE'])
def delete_user_history(user_id):
    """Elimina el historial de chat para un usuario."""
    if Help.delete_chat_history(user_id):
        return jsonify({"mensaje": "Historial eliminado exitosamente"}), 200
    return jsonify({"error": "No se pudo eliminar el historial"}), 500


