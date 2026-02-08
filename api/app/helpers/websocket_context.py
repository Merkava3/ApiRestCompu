"""
WebSocket message context implementation.
"""
import logging
from typing import Optional, Any

from .websocket_interfaces import (
    IMessageContext, IConnectionManager, IMessageFormatter
)

logger = logging.getLogger(__name__)


class WebSocketMessageContext(IMessageContext):
    """Context for WebSocket message handling."""

    def __init__(self,
                 websocket: Any,
                 connection_manager: IConnectionManager,
                 message_formatter: IMessageFormatter,
                 user_id: Optional[str] = None):
        self._websocket = websocket
        self._connection_manager = connection_manager
        self._message_formatter = message_formatter
        self._user_id = user_id

    @property
    def websocket(self) -> Any:
        return self._websocket

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        self._user_id = value

    @property
    def connection_manager(self) -> IConnectionManager:
        return self._connection_manager

    @property
    def message_formatter(self) -> IMessageFormatter:
        return self._message_formatter

    def send_message(self, message: str) -> None:
        try:
            self._websocket.send(message)
        except Exception as e:
            logger.error(f"Send error to {self._user_id}: {e}")

    def send_error(self, error_message: str) -> None:
        try:
            payload = self._message_formatter.create_error(error_message)
            self._websocket.send(payload)
        except Exception as e:
            logger.error(f"Error send error to {self._user_id}: {e}")

    def is_authenticated(self) -> bool:
        return self._user_id is not None

    def get_user_info(self) -> Optional[dict]:
        return self._connection_manager.get_user_info(self._user_id) if self._user_id else None

    def __str__(self) -> str:
        return f"Context(user={self._user_id}, auth={self.is_authenticated()})"
