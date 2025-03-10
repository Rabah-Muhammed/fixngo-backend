from rest_framework import serializers
from .models import Room, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.email', read_only=True)
    room = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'image', 'timestamp']

class RoomSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.email', read_only=True)
    worker = serializers.CharField(source='worker.email', read_only=True)
    participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()  # Added

    class Meta:
        model = Room
        fields = ["id", "user", "worker", "participant", "created_at", "last_message"]

    def get_participant(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        if obj.user == request.user:
            return obj.worker.username
        return obj.user.username

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None