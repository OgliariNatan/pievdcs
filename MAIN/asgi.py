"""
ASGI config for MAIN project.
"""

import os
from django.core.asgi import get_asgi_application

# Configurar o Django ANTES de qualquer import de apps
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MAIN.settings')

# Inicializar o Django primeiro
django_asgi_app = get_asgi_application()

# AGORA podemos importar os módulos que dependem do Django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from mensageria import routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    ),
})