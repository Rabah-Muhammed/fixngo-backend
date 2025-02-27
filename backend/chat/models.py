from django.db import models
from api.models import User


class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rooms')
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worker_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room between {self.user.username} and {self.worker.username}"

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"