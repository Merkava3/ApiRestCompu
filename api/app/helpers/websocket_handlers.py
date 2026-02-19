"""
Message handlers implementing Strategy pattern for WebSocket messages.
"""
import logging
from typing import Dict, Any

from .websocket_interfaces import (
    BaseMessageHandler, IMessageContext, IPersistenceService,
    INotificationService
)
from .const import (
    WS_TYPE_AUTH, WS_TYPE_MESSAGE, WS_SUPPORT_ID,
    WS_ACTION_CLEAN, WS_STATUS_ONLINE
)

logger = logging.getLogger(__name__)


class AuthMessageHandler(BaseMessageHandler):
    """Handles authentication and session setup."""

    def __init__(self, persistence: IPersistenceService, notification: INotificationService):
        super().__init__(WS_TYPE_AUTH)
        self._persistence = persistence
        self._notification = notification

    def _validate_message(self, message: Dict[str, Any]) -> bool:
        return super()._validate_message(message) and message.get('user_id')

    def _process_message(self, message: Dict[str, Any], context: IMessageContext) -> None:
        user_id = message['user_id']
        name = message.get('name', 'Usuario')
        phone = message.get('phone', 'N/A')

        context.connection_manager.add_connection(user_id, context.websocket)
        context.connection_manager.update_user_info(user_id, name, phone)
        context.user_id = user_id

        self._send_history(user_id, context)

        if user_id != WS_SUPPORT_ID:
            self._notification.notify_user_status(user_id, WS_STATUS_ONLINE, name=name, phone=phone)

        logger.info(f"User {user_id} authenticated")

    def _send_history(self, user_id: str, context: IMessageContext) -> None:
        try:
            for row in self._persistence.get_chat_history(user_id):
                sender = row.get("telefono")
                msg = context.message_formatter.create_message(
                    sender_id=sender,
                    receiver_id=row.get("correo_admin", ""),
                    message=row.get("chat", ""),
                    name=row.get("nombres", ""),
                    phone=row.get("telefono", ""),
                    is_history=True
                )
                context.send_message(msg)
        except Exception as e:
            logger.error(f"History send error {user_id}: {e}")
            context.send_error("Failed to load history")


class ChatMessageHandler(BaseMessageHandler):
    """Handles chat routing and persistence."""

    def __init__(self, persistence: IPersistenceService):
        super().__init__(WS_TYPE_MESSAGE)
        self._persistence = persistence

    def _validate_message(self, message: Dict[str, Any]) -> bool:
        return (
            super()._validate_message(message) and
            message.get('message', '').strip() and
            message.get('receiver_id')
        )

    def _process_message(self, message: Dict[str, Any], context: IMessageContext) -> None:
        # MODO LIBRE: Si no hay user_id, asignamos uno por defecto para permitir el chat
        if not context.user_id:
            context.user_id = message.get('user_id') or "usuario_anonimo"
            logger.info(f"⚠️ [MODO LIBRE] Chat permitido sin auth previa para: {context.user_id}")

        text = message.get('message', '').strip()
        receiver_id = message.get('receiver_id')

        if text.lower() == f"/{WS_ACTION_CLEAN}":
            self._handle_clean(receiver_id, context)
        else:
            self._route_message(message, text, receiver_id, context)

    def _handle_clean(self, receiver_id: str, context: IMessageContext) -> None:
        target = context.user_id if context.user_id != WS_SUPPORT_ID else receiver_id
        if self._persistence.delete_chat_history(target):
            cmd = context.message_formatter.create_command(WS_ACTION_CLEAN, user_id=receiver_id)
            context.send_message(cmd)
            target_ws = context.connection_manager.get_connection(receiver_id)
            if target_ws:
                try:
                    target_ws.send(cmd)
                except Exception:
                    pass
        else:
            context.send_error("Clear failed")

    def _route_message(self, message: Dict[str, Any], text: str, receiver_id: str, context: IMessageContext) -> None:
        formatted = context.message_formatter.create_message(
            sender_id=context.user_id,
            message=text,
            receiver_id=receiver_id,
            name=message.get('name', 'Usuario'),
            phone=message.get('phone', 'N/A')
        )

        recipient_ws = context.connection_manager.get_connection(receiver_id)
        if recipient_ws:
            try:
                recipient_ws.send(formatted)
            except Exception as e:
                logger.error(f"Delivery failed to {receiver_id}: {e}")
                context.send_error("Delivery failed")
                return

        self._persistence.save_message(
            sender=context.user_id,
            message=text,
            receiver=receiver_id,
            name=message.get('name', 'Usuario')
        )
        context.send_message(formatted)


class MessageHandlerRegistry:
    """Registry for message handlers."""

    def __init__(self):
        self._handlers = {}

    def register(self, handler: BaseMessageHandler) -> None:
        self._handlers[handler._message_type] = handler

    def handle(self, message: Dict[str, Any], context: IMessageContext) -> bool:
        m_type = message.get('type')
        handler = self._handlers.get(m_type)
        if not handler:
            context.send_error(f"Unknown type: {m_type}")
            return False
        try:
            handler.handle(message, context)
            return True
        except Exception as e:
            logger.error(f"Handler error {m_type}: {e}")
            context.send_error("Server error")
            return False


class MessageHandlerFactory:
    """Factory for message handlers."""

    @classmethod
    def create_registry(cls, persistence: IPersistenceService, notification: INotificationService) -> MessageHandlerRegistry:
        registry = MessageHandlerRegistry()
        registry.register(AuthMessageHandler(persistence, notification))
        registry.register(ChatMessageHandler(persistence))
        return registry
