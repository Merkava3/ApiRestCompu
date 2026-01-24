from flask import request
from ..helpers.helpers import ChatManager
from ..helpers.const import *

def register_chat_handlers(socketio):
    """
    Registra los manejadores de eventos de Socket.IO para el chat.
    Sigue el principio de separación de responsabilidades al desacoplar
    la configuración de Socket.IO de la lógica de negocio.
    """

    @socketio.on('get_active_chats')
    def handle_get_active_chats():
        """
        Envía la lista de chats activos al solicitante (admin).
        """
        chats = ChatManager.get_all_chats()
        active_chats_list = []
        
        for uuid, data in chats.items():
            messages = data.get('messages', [])
            last_msg = messages[-1]['text'] if messages else "Nueva conexión"
            
            active_chats_list.append({
                'uuid': uuid,
                'last_message': last_msg,
                'messages': messages 
            })
            
        socketio.emit(EVENT_CHAT_LIST, {'chats': active_chats_list}, room=request.sid)

    @socketio.on(EVENT_CONNECT)
    @socketio.on(EVENT_CONNECT)
    def handle_connect(auth=None):
        try:
            # En algunas versiones auth viene como argumento, en otras no. 
            # Lo hacemos opcional y también intentamos leerlo del request si es necesario.
            client_uuid = None
            if auth and isinstance(auth, dict):
                client_uuid = auth.get('uuid')
            
            if not client_uuid:
                 client_uuid = ChatManager.generate_uuid()
                 
            sid = request.sid
            
            # Crear o recuperar chat
            chat = ChatManager.create_chat(client_uuid, sid)
            print(f"[CHAT] Nuevo cliente conectado. UUID: {client_uuid} | SID: {sid}")
            
            # Notificar al cliente su UUID asignado
            socketio.emit(EVENT_CONNECT, {'uuid': client_uuid, 'status': 'connected'}, room=sid)
            
            # Notificar a los admins (broadcast)
            try:
                socketio.emit(EVENT_NEW_CHAT, {'uuid': client_uuid}, broadcast=True)
            except TypeError:
                # Fallback si broadcast falla por versión
                socketio.emit(EVENT_NEW_CHAT, {'uuid': client_uuid})
        except Exception as e:
            print(f"[CHAT] Error crítico en handle_connect: {str(e)}")

    @socketio.on(EVENT_CLIENT_MESSAGE)
    def handle_client_message(data):
        """
        Maneja los mensajes enviados por el cliente.
        data debe contener { uuid, message }
        """
        client_uuid = data.get('uuid')
        text = data.get('message')
        
        print(f"[CHAT] Mensaje recibido de {client_uuid}: {text}")

        if not client_uuid or not text:
            return

        # Guardar en memoria
        ChatManager.add_message(client_uuid, 'client', text)
        
        # Emitir a los administradores
        try:
            socketio.emit(EVENT_CLIENT_MESSAGE, {
                'uuid': client_uuid,
                'message': text,
                'sender': 'client'
            }, broadcast=True)
        except TypeError:
            socketio.emit(EVENT_CLIENT_MESSAGE, {
                'uuid': client_uuid,
                'message': text,
                'sender': 'client'
            })

    @socketio.on(EVENT_ADMIN_MESSAGE)
    def handle_admin_message(data):
        """
        Maneja los mensajes enviados por el administrador a un cliente específico.
        data debe contener { uuid, message }
        """
        client_uuid = data.get('uuid')
        text = data.get('message')
        
        print(f"[CHAT] Admin responde a {client_uuid}: {text}")
        
        chat = ChatManager.get_chat(client_uuid)
        if chat and text:
            # Guardar en memoria
            ChatManager.add_message(client_uuid, 'admin', text)
            
            # Emitir solo al cliente específico
            socketio.emit(EVENT_ADMIN_MESSAGE, {
                'message': text,
                'sender': 'admin'
            }, room=chat['sid'])

    @socketio.on(EVENT_DISCONNECT)
    def handle_disconnect():
        """
        Maneja la desconexión de un cliente.
        Elimina el chat de la memoria automáticamente.
        """
        sid = request.sid
        client_uuid = ChatManager.remove_chat_by_sid(sid)
        
        if client_uuid:
            print(f"[CHAT] Cliente desconectado: {client_uuid}")
            try:
                socketio.emit(EVENT_CHAT_CLOSED, {'uuid': client_uuid}, broadcast=True)
            except TypeError:
                socketio.emit(EVENT_CHAT_CLOSED, {'uuid': client_uuid})
