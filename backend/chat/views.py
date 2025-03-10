from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Room, Message
from api.models import Worker, User
from .serializers import RoomSerializer, MessageSerializer

class StartChat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        worker_id = request.data.get('worker_id')
        
        if not worker_id:
            return Response({"error": "Worker ID is required"}, status=400)
        
        worker = get_object_or_404(Worker, id=worker_id)
        if user == worker.user:
            return Response({"error": "You cannot start a chat with yourself"}, status=400)
        
        room, created = Room.objects.get_or_create(user=user, worker=worker.user)
        serializer = RoomSerializer(room, context={'request': request})
        
        return Response({
            "chat_id": room.id,
            "worker_username": worker.user.username,
            "user_email": user.email
        })

class GetChatMessages(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        chat = get_object_or_404(Room, id=chat_id)
        if request.user != chat.user and request.user != chat.worker:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        
        messages = Message.objects.filter(room=chat).order_by("timestamp")
        serializer = MessageSerializer(messages, many=True)
        
        return JsonResponse(serializer.data, safe=False)

class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        room = get_object_or_404(Room, id=chat_id)
        message_text = request.data.get("message", "").strip()
        
        if not message_text:
            return Response({"error": "Message cannot be empty"}, status=400)
        
        message = Message.objects.create(room=room, sender=request.user, content=message_text)
        serializer = MessageSerializer(message)
        
        return Response(serializer.data, status=201)

class GetUserRooms(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        rooms = Room.objects.filter(Q(user=user) | Q(worker=user))
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        
        return Response(serializer.data)