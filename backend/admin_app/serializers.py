# backend/api/views.py
from rest_framework import serializers
from .models import Service
from api.models import Booking,User


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'hourly_rate', 'image', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add other user fields as needed

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nest user details
    service = ServiceSerializer()  # Nest service details

    class Meta:
        model = Booking
        fields = ['id', 'user', 'service', 'worker', 'status', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'created_at' in representation:
            representation['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format date
        return representation
