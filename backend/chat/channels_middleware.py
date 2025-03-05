import json
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from rest_framework.exceptions import AuthenticationFailed
from django.db import close_old_connections
from .jwt_auth import JWTAuth
import logging

logger = logging.getLogger(__name__)

class JWTWebsocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()
        
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_parameters = parse_qs(query_string)
        token = query_parameters.get("token", [None])[0]
        
        if token is None:
            logger.warning("No token provided in WebSocket connection")
            await send({"type": "websocket.send", "text": json.dumps({"error": "Token required"})})
            await send({"type": "websocket.close", "code": 4000})
            return
        
        try:
            user = await JWTAuth.authenticate_websocket(scope, token)
            scope["user"] = user
            logger.info(f"User {user.email} authenticated for WebSocket")
            return await super().__call__(scope, receive, send)
        except AuthenticationFailed as e:
            logger.warning(f"Authentication failed: {str(e)}")
            await send({"type": "websocket.send", "text": json.dumps({"error": str(e)})})
            await send({"type": "websocket.close", "code": 4002})
            return