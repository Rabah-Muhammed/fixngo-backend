from rest_framework import serializers
from .models import User

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
