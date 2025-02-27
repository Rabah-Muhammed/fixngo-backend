# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    user = request.user
    worker_id = request.data.get('worker_id')
    
    room, created = Room.objects.get_or_create(user=user, worker_id=worker_id)
    serializer = RoomSerializer(room)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, room_id):
    messages = Message.objects.filter(room_id=room_id).order_by('timestamp')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_rooms(request):
    user = request.user
    rooms = Room.objects.filter(user=user) | Room.objects.filter(worker=user)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)
