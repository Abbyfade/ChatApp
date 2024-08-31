from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'wss/chat/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'wss/chat-list/', consumers.ChatListConsumer.as_asgi()),
]