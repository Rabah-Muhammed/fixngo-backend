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


class BookingDetailSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    service_id = serializers.IntegerField(source="service.id", read_only=True)
    worker_name = serializers.CharField(source="worker.user.username", read_only=True)
    worker_id = serializers.IntegerField(source="worker.id", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    start_time = serializers.DateTimeField(source="slot.start_time", format="%Y-%m-%d %H:%M:%S", read_only=True)
    end_time = serializers.DateTimeField(source="slot.end_time", format="%Y-%m-%d %H:%M:%S", read_only=True)
    remaining_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    platform_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    completed_at = serializers.DateTimeField(source="updated_at", format="%Y-%m-%d %H:%M:%S", read_only=True)  # ✅ Added completed_at
    transaction_id = serializers.CharField(required=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'service_name', 'worker_name', 'user_name', 'start_time', 'end_time', 'status',
            'service_id', 'worker_id', 'remaining_balance', 'payment_status', 'total_price',
            'platform_fee', 'created_at', 'completed_at', 'transaction_id'
        ]



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    worker = serializers.SlugRelatedField(slug_field='user__username', queryset=Worker.objects.all())
    service_name = serializers.CharField(source='booking.service.name', read_only=True)  # Added service_name

    class Meta:
        model = Review
        fields = ['id', 'user', 'worker', 'rating', 'review', 'service_name', 'booking', 'created_at']