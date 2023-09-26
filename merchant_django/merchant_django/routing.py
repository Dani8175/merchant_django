from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from carrot_app.consumers import ChatConsumer

application = ProtocolTypeRouter(
    {
        "websocket": URLRouter(
            [
                path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi()),
            ]
        ),
    }
)
