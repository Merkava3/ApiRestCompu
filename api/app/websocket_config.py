"""
WebSocket configuration module.
"""
import json
import logging
from typing import Optional, Dict, Any

from simple_websocket.ws import ConnectionClosed

from .helpers.websocket_services import WebSocketServiceFactory
from .helpers.websocket_handlers import MessageHandlerFactory
from .helpers.websocket_context import WebSocketMessageContext
from .helpers.const import WS_STATUS_OFFLINE

# Configure logging
logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Manages a single WebSocket connection lifecycle."""

    def __init__(self, websocket, services: Dict[str, Any]):
        self._websocket = websocket
        self._services = services
        self._context = WebSocketMessageContext(
            websocket=self._websocket,
            connection_manager=self._services['connection_manager'],
            message_formatter=self._services['message_formatter']
        )
        self._registry = MessageHandlerFactory.create_registry(
            persistence=self._services['persistence_service'],
            notification=self._services['notification_service']
        )
        self._user_id: Optional[str] = None

    def handle_connection(self) -> None:
        try:
            while True:
                raw = self._websocket.receive()
                if not raw:
                    break
                self._process_message(raw)
        except ConnectionClosed:
            logger.info(f"Closed for {self._user_id}")
        except Exception as e:
            logger.error(f"Error for {self._user_id}: {e}")
        finally:
            self._cleanup()

    def _process_message(self, raw: str) -> None:
        try:
            msg = json.loads(raw)
            if not isinstance(msg, dict):
                return
            
            # Sync context user_id
            self._context.user_id = self._user_id
            
            if self._registry.handle(msg, self._context):
                # Update local user_id if changed (e.g. after auth)
                if self._context.user_id and not self._user_id:
                    self._user_id = self._context.user_id
        except json.JSONDecodeError:
            self._context.send_error("Invalid JSON")
        except Exception as e:
            logger.error(f"Process error: {e}")

    def _cleanup(self) -> None:
        if self._user_id:
            self._services['connection_manager'].remove_connection(self._user_id)
            self._services['notification_service'].notify_user_status(
                user_id=self._user_id,
                status=WS_STATUS_OFFLINE
            )


class WebSocketManager:
    """Configures and manages WebSocket system."""

    def __init__(self):
        self._services = None
        self._app = None

    def initialize(self, app) -> bool:
        self._app = app
        try:
            from flask_sock import Sock
            self._services = WebSocketServiceFactory.create_service_container()
            
            # Init DB
            from .helpers.helpers import Help
            Help.init_chat_db()

            sock = Sock(app)
            @sock.route("/api/v1/chat")
            def chat_endpoint(ws):
                WebSocketConnection(ws, self._services).handle_connection()

            logger.info("WebSocket system initialized")
            return True
        except Exception as e:
            logger.error(f"Init failed: {e}")
            return False

    def get_diagnostics(self) -> Dict[str, Any]:
        if not self._services:
            return {"status": "not_configured"}
        return self._services['health_check_service'].get_system_status()


# Public API
def init_websocket(app) -> bool:
    return WebSocketManager().initialize(app)


def check_websocket_health() -> Dict[str, Any]:
    return WebSocketManager().get_diagnostics()
