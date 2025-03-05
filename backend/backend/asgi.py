import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns
from chat.channels_middleware import JWTWebsocketMiddleware
from channels.layers import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django.setup()

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTWebsocketMiddleware(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)