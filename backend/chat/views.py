from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Room, Message
from api.models import Worker, User
from django.shortcuts import get_object_or_404
from .serializers import RoomSerializer, MessageSerializer
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db.models import Q

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chat(request):
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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, chat_id):
    chat = get_object_or_404(Room, id=chat_id)
    if request.user != chat.user and request.user != chat.worker:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    messages = Message.objects.filter(room=chat).order_by("timestamp")
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse(serializer.data, safe=False)

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, chat_id):
        room = get_object_or_404(Room, id=chat_id)
        message_text = request.data.get("message", "").strip()
        if not message_text:
            return Response({"error": "Message cannot be empty"}, status=400)
        message = Message.objects.create(room=room, sender=request.user, content=message_text)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_rooms(request):
    user = request.user
    rooms = Room.objects.filter(Q(user=user) | Q(worker=user))
    serializer = RoomSerializer(rooms, many=True, context={'request': request})
    return Response(serializer.data)