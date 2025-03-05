from rest_framework import serializers
from .models import Room, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class RoomSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.email', read_only=True)
    worker = serializers.CharField(source='worker.email', read_only=True)
    participant = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "user", "worker", "participant", "created_at"]

    def get_participant(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        if obj.user == request.user:
            return obj.worker.username
        return obj.user.username

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.email', read_only=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(allow_null=True, required=False)  # Include image field

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'image', 'timestamp']