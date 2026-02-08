"""
Concrete implementations of WebSocket services following SOLID principles.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .websocket_interfaces import (
    IConnectionManager, IUserInfoManager, IMessageFormatter,
    IPersistenceService, INotificationService, IHealthCheckService
)
from .const import (
    WS_SUPPORT_ID, WS_TYPE_MESSAGE, WS_TYPE_COMMAND, WS_TYPE_ERROR,
    WS_ACTION_STATUS
)
from .helpers import Help

# Configure logging
logger = logging.getLogger(__name__)


class ConnectionInfo:
    """Value object for connection information."""

    def __init__(self, user_id: str, websocket: Any, name: str = "Unknown", phone: str = "N/A"):
        self._user_id = user_id
        self._websocket = websocket
        self._name = name
        self._phone = phone
        self._connected_at = datetime.now()

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def websocket(self) -> Any:
        return self._websocket

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def connected_at(self) -> datetime:
        return self._connected_at

    def with_updated_info(self, name: str = None, phone: str = None) -> 'ConnectionInfo':
        return ConnectionInfo(
            self._user_id,
            self._websocket,
            name or self._name,
            phone or self._phone
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self._user_id,
            'name': self._name,
            'phone': self._phone,
            'connected_at': self._connected_at.isoformat(),
            'socket': self._websocket
        }


class WebSocketConnectionManager(IConnectionManager, IUserInfoManager):
    """
    Concrete implementation of connection and user info management.
    Implements Singleton pattern.
    """
    _instance = None
    _connections: Dict[str, ConnectionInfo] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_connection(self, user_id: str, websocket: Any) -> None:
        self._connections[user_id] = ConnectionInfo(user_id, websocket)
        logger.info(f"User {user_id} connected. Total: {len(self._connections)}")

    def remove_connection(self, user_id: str) -> None:
        if user_id in self._connections:
            del self._connections[user_id]
            logger.info(f"User {user_id} disconnected. Total: {len(self._connections)}")

    def get_connection(self, user_id: str) -> Optional[Any]:
        connection_info = self._connections.get(user_id)
        return connection_info.websocket if connection_info else None

    def is_connected(self, user_id: str) -> bool:
        return user_id in self._connections

    def get_all_connections(self) -> Dict[str, Any]:
        return {
            u_id: info.to_dict()
            for u_id, info in self._connections.items()
        }

    def update_user_info(self, user_id: str, name: str = None, phone: str = None) -> None:
        if user_id in self._connections:
            self._connections[user_id] = self._connections[user_id].with_updated_info(name, phone)

    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        info = self._connections.get(user_id)
        if info:
            return {
                'name': info.name,
                'phone': info.phone,
                'connected_at': info.connected_at
            }
        return None


class JsonMessageFormatter(IMessageFormatter):
    """JSON implementation of message formatting."""

    def create_message(self, sender_id: str, message: str, **kwargs) -> str:
        payload = {
            "type": WS_TYPE_MESSAGE,
            "sender_id": sender_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        for key in ['receiver_id', 'name', 'phone', 'is_history']:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = kwargs[key]
        return json.dumps(payload)

    def create_command(self, action: str, **kwargs) -> str:
        payload = {"type": WS_TYPE_COMMAND, "action": action}
        for key in ['user_id', 'status', 'name', 'phone']:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = kwargs[key]
        return json.dumps(payload)

    def create_error(self, message: str) -> str:
        return json.dumps({
            "type": WS_TYPE_ERROR,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def create_status_change(self, user_id: str, status: str, **kwargs) -> str:
        return self.create_command(
            action=WS_ACTION_STATUS,
            user_id=user_id,
            status=status,
            **kwargs
        )


class ChatPersistenceService(IPersistenceService):
    """Persistence using Help class."""

    def save_message(self, sender: str, message: str, receiver: str, **kwargs) -> bool:
        try:
            Help.save_chat_message(
                nombres=kwargs.get('name', 'Usuario'),
                telefono=sender,
                chat=message,
                correo_admin=receiver
            )
            return True
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False

    def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            return Help.get_chat_history(user_id) or []
        except Exception as e:
            logger.error(f"History error {user_id}: {e}")
            return []

    def delete_chat_history(self, user_id: str) -> bool:
        try:
            Help.delete_chat_history(user_id)
            return True
        except Exception as e:
            logger.error(f"Delete error {user_id}: {e}")
            return False


class SupportNotificationService(INotificationService):
    """Support notifications."""

    def __init__(self, connection_manager: IConnectionManager, formatter: IMessageFormatter):
        self._manager = connection_manager
        self._formatter = formatter

    def notify_user_status(self, user_id: str, status: str, **kwargs) -> None:
        if user_id == WS_SUPPORT_ID:
            return
        support_ws = self._manager.get_connection(WS_SUPPORT_ID)
        if support_ws:
            try:
                msg = self._formatter.create_status_change(user_id, status, **kwargs)
                support_ws.send(msg)
            except Exception as e:
                logger.error(f"Notify error: {e}")

    def notify_support(self, message: str, user_id: str = None) -> None:
        support_ws = self._manager.get_connection(WS_SUPPORT_ID)
        if support_ws:
            try:
                msg = self._formatter.create_message("system", message, receiver_id=WS_SUPPORT_ID, name="System")
                support_ws.send(msg)
            except Exception as e:
                logger.error(f"Support notify error: {e}")


class WebSocketHealthCheckService(IHealthCheckService):
    """Health check for WebSocket."""

    def __init__(self, manager: IConnectionManager):
        self._manager = manager

    def check_dependencies(self) -> Dict[str, Any]:
        return {
            "flask_sock": self._importable("flask_sock"),
            "simple_websocket": self._importable("simple_websocket"),
            "chat_db": self._check_db()
        }

    def get_system_status(self) -> Dict[str, Any]:
        deps = self.check_dependencies()
        conns = self._manager.get_all_connections()
        return {
            "status": "healthy" if all(deps.values()) else "error",
            "timestamp": datetime.now().isoformat(),
            "dependencies": deps,
            "active_connections": len(conns),
            "connection_details": conns
        }

    def _importable(self, name: str) -> bool:
        try:
            __import__(name)
            return True
        except ImportError:
            return False

    def _check_db(self) -> bool:
        try:
            Help.init_chat_db()
            return True
        except Exception:
            return False


class WebSocketServiceFactory:
    """Factory for WebSocket services."""

    @staticmethod
    def create_service_container() -> Dict[str, Any]:
        manager = WebSocketConnectionManager()
        formatter = JsonMessageFormatter()
        persistence = ChatPersistenceService()
        notification = SupportNotificationService(manager, formatter)
        health = WebSocketHealthCheckService(manager)

        return {
            'connection_manager': manager,
            'message_formatter': formatter,
            'persistence_service': persistence,
            'notification_service': notification,
            'health_check_service': health
        }
