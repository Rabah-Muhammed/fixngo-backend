from django.urls import path
from .views import get_chat_messages, start_chat, SendMessageView, get_user_rooms


urlpatterns = [
    path('start-chat/', start_chat, name='start_chat'),
    path('<int:chat_id>/messages/', get_chat_messages, name='get_chat_messages'),
    path('<int:chat_id>/send-message/', SendMessageView.as_view(), name='send_message'),
    path('rooms/', get_user_rooms, name='get_user_rooms'),
   
]