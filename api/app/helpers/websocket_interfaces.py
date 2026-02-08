"""
WebSocket interfaces and abstract classes following SOLID principles.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class IConnectionManager(ABC):
    """Interface for managing WebSocket connections."""

    @abstractmethod
    def add_connection(self, user_id: str, websocket: Any) -> None:
        """Register a new WebSocket connection."""
        pass

    @abstractmethod
    def remove_connection(self, user_id: str) -> None:
        """Remove a WebSocket connection."""
        pass

    @abstractmethod
    def get_connection(self, user_id: str) -> Optional[Any]:
        """Get WebSocket connection for a user."""
        pass

    @abstractmethod
    def is_connected(self, user_id: str) -> bool:
        """Check if user is connected."""
        pass

    @abstractmethod
    def get_all_connections(self) -> Dict[str, Any]:
        """Get all active connections."""
        pass


class IUserInfoManager(ABC):
    """Interface for managing user information."""

    @abstractmethod
    def update_user_info(self, user_id: str, name: str = None, phone: str = None) -> None:
        """Update user information."""
        pass

    @abstractmethod
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information."""
        pass


class IMessageFormatter(ABC):
    """Interface for message formatting."""

    @abstractmethod
    def create_message(self, sender_id: str, message: str, **kwargs) -> str:
        """Create a formatted message."""
        pass

    @abstractmethod
    def create_command(self, action: str, **kwargs) -> str:
        """Create a formatted command."""
        pass

    @abstractmethod
    def create_error(self, message: str) -> str:
        """Create a formatted error message."""
        pass

    @abstractmethod
    def create_status_change(self, user_id: str, status: str, **kwargs) -> str:
        """Create a status change notification."""
        pass


class IMessageHandler(ABC):
    """Interface for handling different types of messages."""

    @abstractmethod
    def can_handle(self, message_type: str) -> bool:
        """Check if this handler can process the message type."""
        pass

    @abstractmethod
    def handle(self, message: Dict[str, Any], context: 'IMessageContext') -> None:
        """Handle the message."""
        pass


class IMessageContext(ABC):
    """Context interface for message handling."""

    @property
    @abstractmethod
    def websocket(self) -> Any:
        """Get the WebSocket connection."""
        pass

    @property
    @abstractmethod
    def user_id(self) -> Optional[str]:
        """Get the current user ID."""
        pass

    @user_id.setter
    @abstractmethod
    def user_id(self, value: str) -> None:
        """Set the user ID."""
        pass

    @property
    @abstractmethod
    def connection_manager(self) -> IConnectionManager:
        """Get the connection manager."""
        pass

    @property
    @abstractmethod
    def message_formatter(self) -> IMessageFormatter:
        """Get the message formatter."""
        pass

    @abstractmethod
    def send_message(self, message: str) -> None:
        """Send a message through the WebSocket."""
        pass

    @abstractmethod
    def send_error(self, error_message: str) -> None:
        """Send an error message."""
        pass


class IPersistenceService(ABC):
    """Interface for chat persistence operations."""

    @abstractmethod
    def save_message(self, sender: str, message: str, receiver: str, **kwargs) -> bool:
        """Save a chat message."""
        pass

    @abstractmethod
    def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a user."""
        pass

    @abstractmethod
    def delete_chat_history(self, user_id: str) -> bool:
        """Delete chat history for a user."""
        pass


class INotificationService(ABC):
    """Interface for notification services."""

    @abstractmethod
    def notify_user_status(self, user_id: str, status: str, **kwargs) -> None:
        """Notify about user status changes."""
        pass

    @abstractmethod
    def notify_support(self, message: str, user_id: str = None) -> None:
        """Send notification to support."""
        pass


class IHealthCheckService(ABC):
    """Interface for health check operations."""

    @abstractmethod
    def check_dependencies(self) -> Dict[str, Any]:
        """Check system dependencies."""
        pass

    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        pass


class BaseMessageHandler(IMessageHandler):
    """Base implementation for message handlers."""

    def __init__(self, message_type: str):
        self._message_type = message_type

    def can_handle(self, message_type: str) -> bool:
        return message_type == self._message_type

    def handle(self, message: Dict[str, Any], context: IMessageContext) -> None:
        if not self._validate_message(message):
            context.send_error("Invalid message format")
            return

        self._process_message(message, context)

    def _validate_message(self, message: Dict[str, Any]) -> bool:
        return isinstance(message, dict) and 'type' in message

    @abstractmethod
    def _process_message(self, message: Dict[str, Any], context: IMessageContext) -> None:
        pass
