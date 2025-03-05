import json
import base64
from io import BytesIO
from django.core.files.base import ContentFile
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from api.models import User
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        user = self.scope['user']
        if not await self.is_valid_participant(user):
            await self.send(text_data=json.dumps({'error': 'Unauthorized'}))
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        messages = await self.get_initial_messages()
        await self.send(text_data=json.dumps({'messages': messages}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        image_data = data.get('image', None)  # Expect base64 string

        room = await self.get_room()
        if not room:
            await self.send(text_data=json.dumps({'error': 'Room not found'}))
            return

        message_obj = await self.save_message(room, self.scope['user'], message, image_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': self.scope['user'].email,
                'message': message_obj.content,
                'image': message_obj.image.url if message_obj.image else None,
                'timestamp': message_obj.timestamp.isoformat(),
                'id': message_obj.id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'image': event['image'],
            'timestamp': event['timestamp'],
            'id': event['id'],
        }))

    @database_sync_to_async
    def is_valid_participant(self, user):
        room = Room.objects.get(id=self.room_id)
        return user == room.user or user == room.worker

    @database_sync_to_async
    def get_room(self):
        return Room.objects.filter(id=self.room_id).first()

    @database_sync_to_async
    def get_initial_messages(self):
        room = Room.objects.get(id=self.room_id)
        messages = Message.objects.filter(room=room).order_by("timestamp")
        return [
            {
                'id': m.id,
                'sender': m.sender.email,
                'content': m.content,
                'image': m.image.url if m.image else None,
                'timestamp': m.timestamp.isoformat()
            } for m in messages
        ]

    @database_sync_to_async
    def save_message(self, room, sender, message, image_data):
        message_obj = Message(room=room, sender=sender, content=message)
        if image_data:
            # Decode base64 image and save it
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"image_{message_obj.id}.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=file_name)
            message_obj.image.save(file_name, data, save=True)
        message_obj.save()
        return message_obj