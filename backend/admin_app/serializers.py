from rest_framework import serializers
from api.models import Booking, User, Review, Worker, Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'hourly_rate', 'image', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class WorkerSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Include worker's user details

    class Meta:
        model = Worker
        fields = ['id', 'user']  # Removed `experience` if it doesn't exist in the model


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    service = ServiceSerializer()
    worker = WorkerSerializer(read_only=True)  # Handle worker details correctly

    class Meta:
        model = Booking
        fields = ['id', 'user', 'service', 'worker', 'status', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'created_at' in representation:
            representation['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return representation



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    worker = serializers.SlugRelatedField(slug_field='user__username', queryset=Worker.objects.all())
    service_name = serializers.CharField(source='booking.service.name', read_only=True)  # Added service_name

    class Meta:
        model = Review
        fields = ['id', 'user', 'worker', 'rating', 'review', 'service_name', 'booking', 'created_at']