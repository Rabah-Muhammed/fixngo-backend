import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set the settings module and initialize Django first
settings_module = 'backend.deployment_settings' if 'RENDER_EXTERNAL_HOSTNAME' in os.environ else 'backend.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

# Now safe to import Django-dependent modules
from chat.routing import websocket_urlpatterns
from chat.channels_middleware import JWTWebsocketMiddleware
from channels.layers import get_channel_layer  # Unused, but safe to keep here

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTWebsocketMiddleware(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)