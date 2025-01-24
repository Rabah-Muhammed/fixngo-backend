from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer,UserProfileSerializer
from .tokens import CustomRefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from .utils import (generate_otp, send_otp_to_email, store_otp_in_cache, 
    get_otp_from_cache,get_id_token_with_code_method_1,get_id_token_with_code_method_2)
from .serializers import RequestPasswordResetSerializer, ResetPasswordSerializer
from django.core.cache import cache
from django.core.mail import send_mail
import random

User = get_user_model()

class SignupView(APIView):
    permission_classes = [AllowAny]  # Ensure this endpoint is publicly accessible

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = generate_otp()
            store_otp_in_cache(user.email, otp)
            send_otp_to_email(user.email, otp)
            return Response({"message": "User registered successfully. OTP sent to email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]  # Ensure unauthenticated access

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the OTP from the cache
        cached_otp = cache.get(email)

        if cached_otp is None:
            return Response({"error": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        if cached_otp == otp:
            try:
                # Update the is_verified field for the user
                user = User.objects.get(email=email)
                user.is_verified = True
                user.save()

                # Clear the OTP from the cache after successful verification
                cache.delete(email)

                return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)


class ResendOtpAPIView(APIView):
    permission_classes = [AllowAny]  # Ensure unauthenticated access

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=400)

        # Generate a new OTP
        otp = generate_otp()

        # Store the OTP in the cache with a 5-minute timeout
        cache.set(email, otp, timeout=300)

        # Send the OTP to the email
        try:
            send_otp_to_email(email, otp)
            return Response({"message": "OTP resent successfully."}, status=200)
        except Exception as e:
            return Response({"error": f"Failed to send OTP: {str(e)}"}, status=500)
        
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)

        if user:
            if not user.is_verified:
                return Response({"error": "Your account is not verified. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)

            refresh = CustomRefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                }
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)  # Generate OTP for password reset
            cache.set(email, otp, timeout=600)  # Store OTP in cache for 10 minutes

            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP for password reset is: {otp}",
                from_email="noreply@example.com",
                recipient_list=[email],
            )

            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"error": "Email not registered."}, status=status.HTTP_404_NOT_FOUND)

User = get_user_model()

def generate_otp():
    return str(random.randint(100000, 999999))  # Generates a 6-digit OTP


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                otp = generate_otp()
                cache.set(email, otp, timeout=300)  # Cache OTP for 5 minutes

                # Send OTP via email
                send_mail(
                    "Password Reset OTP",
                    f"Your OTP for password reset is {otp}",
                    "no-reply@example.com",  # Use your actual email address
                    [email],
                )
                return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['password']

            cached_otp = cache.get(email)

            if cached_otp == otp:
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    cache.delete(email)  # Remove OTP from cache
                    return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def authenticate_or_create_user(email, username=None):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Use username from Google (if provided), otherwise fallback to email
        if not username:
            username = email  # Fallback to email if no username is provided
        user = User.objects.create_user(username=username, email=email, role='USER')
    return user

class LoginWithGoogle(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if 'code' in request.data.keys():
            code = request.data['code']
            id_token = get_id_token_with_code_method_2(code)
            if not id_token:
                return Response({'error': 'Invalid Google token'}, status=400)

            user_email = id_token['email']
            user_username = id_token.get('name', user_email)  # Use Google account name as username
            user = authenticate_or_create_user(user_email, user_username)

            # Create custom access and refresh tokens for the user with additional claims
            access_token = CustomRefreshToken.for_user(user)
            refresh_token = CustomRefreshToken.for_user(user)

            # Return both access token and refresh token
            return Response({
                'access_token': str(access_token),  # Return access token
                'refresh_token': str(refresh_token),  # Return refresh token
                'username': user_username,  # Return username
                'role': user.role,  # Return role
                'email': user_email  # Return email
            })

        return Response('Code not provided', status=400)
    
    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the authenticated user's profile data.
        """
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update the authenticated user's profile data.
        """
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)