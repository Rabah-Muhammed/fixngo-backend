# worker_app/serializers.py
from rest_framework import serializers
from api.models import User,Worker
from .models import Service

class WorkerSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password']
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
        validated_data.pop('confirm_password')
        validated_data['role'] = 'WORKER'  # Automatically assign role as 'WORKER'
        user = User.objects.create_user(**validated_data)
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
    
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'price', 'duration']