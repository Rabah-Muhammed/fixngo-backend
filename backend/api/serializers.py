from django.conf import settings
from rest_framework import serializers
from .models import Booking, Review,User,Worker,Slot, WorkerWallet
from admin_app.models import Service
from django.utils.timezone import now


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)  # Adding confirm_password field

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password']  # Don't include role in the frontend form
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """
        Ensure that the password and confirm password match.
        """
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        return attrs

    def create(self, validated_data):
        """
        Create a user with the validated data and automatically set the role to 'USER'.
        """
        validated_data.pop('confirm_password')  # Remove confirm_password from validated data
        validated_data['role'] = 'USER'  # Automatically assign the role as 'USER'
        user = User.objects.create_user(**validated_data)
        return user
    
class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=8)
    


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'phone_number', 'profile_picture',
            'date_of_birth', 'gender', 'address', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['email', 'is_verified', 'date_joined']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'hourly_rate', 'image', 'created_at', 'updated_at']

class WorkerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    profile_picture = serializers.ImageField(source="user.profile_picture", read_only=True)
    services = ServiceSerializer(many=True, read_only=True)  # Include related services

    class Meta:
        model = Worker
        fields = [
            "id", "username", "email", "phone_number", "profile_picture",
            "service_area", "availability_status", "rating", "completed_jobs",
            "services"
        ]

class WorkerSlotSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(read_only=True)  # Embed worker details

    class Meta:
        model = Slot
        fields = ['id', 'worker', 'start_time', 'end_time', 'is_available']
        
        
class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    service_id = serializers.IntegerField(source="service.id", read_only=True)
    worker_name = serializers.CharField(source="worker.user.username", read_only=True)
    worker_id = serializers.IntegerField(source="worker.id", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)  # ✅ Added user_name
    start_time = serializers.DateTimeField(source="slot.start_time", format="%Y-%m-%d %H:%M:%S", read_only=True)
    end_time = serializers.DateTimeField(source="slot.end_time", format="%Y-%m-%d %H:%M:%S", read_only=True)
    remaining_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    platform_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    completed_at = serializers.DateTimeField(source="updated_at", format="%Y-%m-%d %H:%M:%S", read_only=True)  # ✅ Added completed_at

    class Meta:
        model = Booking
        fields = [
            'id', 'service_name', 'worker_name', 'user_name', 'start_time', 'end_time', 'status',
            'service_id', 'worker_id', 'remaining_balance', 'payment_status', 'total_price',
            'platform_fee', 'created_at', 'completed_at'
        ]

        


class WorkerWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerWallet
        fields = ["balance", "updated_at"]
        
        

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    worker_name = serializers.SerializerMethodField()  # New field for worker's name

    class Meta:
        model = Review
        fields = ["id", "user_name", "worker_name", "rating", "review", "created_at"]

    def get_user_name(self, obj):
        return obj.user.username if obj.user.username else "Anonymous User"

    def get_worker_name(self, obj):
        return obj.worker.user.username if obj.worker.user.username else "Anonymous Worker"


class VisitWorkerProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    profile_picture = serializers.SerializerMethodField()
    gender = serializers.CharField(source="user.gender", read_only=True)

    class Meta:
        model = Worker
        fields = [
            "id", "username", "user_email", "phone_number", "profile_picture", "gender",
            "service_area", "availability_status", "completed_jobs"
        ]

    def get_profile_picture(self, obj):
        if obj.user.profile_picture:
            return f"{settings.MEDIA_URL}{obj.user.profile_picture}"
        return None



############################################################################# workers related serializers


class WorkerSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    service_area = serializers.CharField(required=True)  # Added service_area field

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password', 'service_area']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password as it's not needed in the User model
        
        # Pop the service_area field from validated data
        service_area = validated_data.pop('service_area')

        # Set role as 'WORKER'
        validated_data['role'] = 'WORKER'  # Automatically assign role as 'WORKER'

        # Create the User without the service_area field
        user = User.objects.create_user(**validated_data)

        # Now create the Worker profile with the service_area field
        Worker.objects.create(user=user, service_area=service_area)

        return user



class WorkerProfileSerializer(serializers.ModelSerializer):
    # User-related fields
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", required=False)
    profile_picture = serializers.ImageField(source="user.profile_picture", required=False)
    address = serializers.CharField(source="user.address", required=False)
    date_of_birth = serializers.DateField(source="user.date_of_birth", required=False)
    gender = serializers.CharField(source="user.gender", required=False)
    date_joined = serializers.DateTimeField(source="user.date_joined", read_only=True)  # Added date_joined field

    class Meta:
        model = Worker
        fields = [
            "username",
            "email",
            "phone_number",
            "profile_picture",
            "address",
            "skills",
            "service_area",
            "availability_status",
            "date_of_birth",  # Added date_of_birth field
            "gender", 
            "date_joined",  # Added date_joined field
        ]

    def update(self, instance, validated_data):
        # Extract user-related data from validated data
        user_data = validated_data.pop("user", {})

        # Update user fields
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if value is not None:  # Only update if the value is provided
                    setattr(user, attr, value)
            user.save()

        # Update worker-specific fields
        for attr, value in validated_data.items():
            if value is not None:  # Ensure we only update with non-null values
                setattr(instance, attr, value)
        instance.save()

        return instance
    
    


class WorkerServiceSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), many=True)

    class Meta:
        model = Worker
        fields = ['services']
        
        
class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['id', 'worker', 'start_time', 'end_time', 'is_available']

    def validate(self, data):
        """Ensure slots do not overlap."""
        worker = data["worker"]
        start_time = data["start_time"]
        end_time = data["end_time"]

        if end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time.")

        if start_time < now():
            raise serializers.ValidationError("You cannot create slots in the past.")

        # Check if the slot overlaps with an existing slot
        overlapping_slots = Slot.objects.filter(
            worker=worker,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

        if overlapping_slots:
            raise serializers.ValidationError("This slot overlaps with an existing slot.")

        return data
        
        

class WorkerBookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    worker_name = serializers.CharField(source="worker.user.username", read_only=True)
    start_time = serializers.DateTimeField(source="slot.start_time", format="%Y-%m-%d %I:%M %p", read_only=True)
    end_time = serializers.DateTimeField(source="slot.end_time", format="%Y-%m-%d %I:%M %p", read_only=True)
    price = serializers.DecimalField(source="service.price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "service_name", "user_name", "worker_name", "start_time", "end_time", "status", "price"]



