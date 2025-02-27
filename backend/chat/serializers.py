from rest_framework import serializers
from .models import Room, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class RoomSerializer(serializers.ModelSerializer):
    participant = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "user", "worker", "created_at", "participant"]

    def get_participant(self, obj):
        request_user = self.context["request"].user
        participant = obj.worker if request_user == obj.user else obj.user
        return {"id": participant.id, "username": participant.username}

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "sender_username", "content", "timestamp"]
