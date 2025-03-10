from django.urls import path
from .views import GetChatMessages, StartChat, SendMessage, GetUserRooms


urlpatterns = [
    path('start-chat/', StartChat.as_view(), name='start_chat'),
    path('<int:chat_id>/messages/', GetChatMessages.as_view(), name='get_chat_messages'),
    path('<int:chat_id>/send-message/', SendMessage.as_view(), name='send_message'),
    path('rooms/', GetUserRooms.as_view(), name='get_user_rooms'),
   
]