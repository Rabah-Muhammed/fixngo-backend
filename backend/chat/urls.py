from django.urls import path
from .views import create_room, get_messages, get_user_rooms

urlpatterns = [
    path("create-room/", create_room, name="create-room"),
    path("messages/<int:room_id>/", get_messages, name="get-messages"),
    path("chat-rooms/", get_user_rooms, name="chat-rooms"),
]
