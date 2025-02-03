from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,views
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Booking, User,Worker,Slot
from .serializers import (BookingSerializer, SlotSerializer, UserSerializer,UserProfileSerializer, WorkerSerializer,WorkerSignupSerializer,
                          WorkerProfileSerializer,ServiceSerializer,WorkerServiceSerializer, WorkerSlotSerializer)
from .tokens import CustomRefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from .utils import (generate_otp, send_otp_to_email, store_otp_in_cache, 
    get_otp_from_cache,get_id_token_with_code_method_1,get_id_token_with_code_method_2)
from .serializers import RequestPasswordResetSerializer, ResetPasswordSerializer
from django.core.cache import cache
from django.core.mail import send_mail
from admin_app.models import Service
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
    

class UserServiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Get all the services available for the user
        services = Service.objects.all().order_by('-created_at')
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserServiceDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        serializer = ServiceSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ServiceWorkersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, service_id):
        try:
            service = Service.objects.get(id=service_id)
            workers = Worker.objects.filter(services=service)
            serializer = WorkerSerializer(workers, many=True)
            return Response({"workers": serializer.data}, status=200)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=404)
        
# Get available slots for a worker
class WorkerSlotPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, worker_id):
        worker = get_object_or_404(Worker, id=worker_id)
        available_slots = Slot.objects.filter(worker=worker, is_available=True)
        serializer = WorkerSlotSerializer(available_slots, many=True)
        return Response({"slots": serializer.data}, status=status.HTTP_200_OK)

# Create booking
class BookingCreateView(APIView):
    def post(self, request):
        worker_id = request.data.get("worker")
        slot_id = request.data.get("slot")
        service_id = request.data.get("service")
        user = request.user

        # Ensure all fields are provided
        if not worker_id or not slot_id or not service_id:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            worker = Worker.objects.get(id=worker_id)
            slot = Slot.objects.get(id=slot_id, is_available=True)
            service = Service.objects.get(id=service_id)

            # Create the booking
            booking = Booking.objects.create(user=user, worker=worker, slot=slot, service=service, status="Confirmed")
            slot.is_available = False
            slot.save()

            return Response({"message": "Booking successful", "booking_id": booking.id}, status=status.HTTP_201_CREATED)

        except Worker.DoesNotExist:
            return Response({"error": "Worker not found"}, status=status.HTTP_404_NOT_FOUND)
        except Slot.DoesNotExist:
            return Response({"error": "Slot not available or does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)



class BookingListView(APIView):
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingDetailView(APIView):
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)


class CancelBookingView(APIView):
    def patch(self, request, booking_id):
        try:
            # Get the booking
            booking = Booking.objects.get(id=booking_id)

            # Update booking status to 'cancelled'
            booking.status = 'cancelled'
            booking.save()

            # Find the related slot and mark it as available
            slot = booking.slot
            slot.is_booked = False
            slot.is_available = True
            slot.save()

            return Response(
                {"message": "Booking canceled successfully", "status": "cancelled"},
                status=status.HTTP_200_OK,
            )
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
    
##################################################################################### workers related views
    

class WorkerSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WorkerSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()  # Create the user and worker profile
            return Response({"message": "Worker created successfully!"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class WorkerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        # Authenticate the worker
        user = authenticate(email=email, password=password)

        if user and user.role == 'WORKER':  # Make sure the user is a worker
            # Generate custom tokens with additional claims
            refresh = CustomRefreshToken.for_user(user)  # Correctly call for_user() method
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
    
    
class WorkerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure the logged-in user is a worker
        if request.user.role != 'WORKER':
            return Response({"error": "You do not have permission to view this page."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve the worker profile (or related data)
        worker = Worker.objects.get(user=request.user)
        return Response({
            "username": worker.user.username,
            "email": worker.user.email,
            "phone_number": worker.user.phone_number,
        }, status=status.HTTP_200_OK)
        

class WorkerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "WORKER":
            return Response({"error": "You are not authorized to view this profile."}, status=status.HTTP_403_FORBIDDEN)
        try:
            worker = Worker.objects.get(user=request.user)
            serializer = WorkerProfileSerializer(worker)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Worker.DoesNotExist:
            return Response({"error": "Worker profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        if request.user.role != "WORKER":
            return Response({"error": "You are not authorized to update this profile."}, status=status.HTTP_403_FORBIDDEN)
        try:
            worker = Worker.objects.get(user=request.user)
            serializer = WorkerProfileSerializer(worker, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Worker.DoesNotExist:
            return Response({"error": "Worker profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
 
class WorkerServicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            worker = Worker.objects.get(user=request.user)
            services = Service.objects.all()
            return Response({
                "available_services": [{"id": s.id, "name": s.name} for s in services],
                "selected_services": [{"id": s.id, "name": s.name} for s in worker.services.all()],
            }, status=200)
        except Worker.DoesNotExist:
            return Response({"error": "Worker not found."}, status=404)


class WorkerServiceUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        worker = get_object_or_404(Worker, user=request.user)
        service_ids = request.data.get("services", [])
        services = Service.objects.filter(id__in=service_ids)
        
        if not services:
            return Response({"error": "No valid services found."}, status=400)

        worker.services.set(services)
        worker.save()
        return Response({"message": "Services updated successfully."}, status=200)

class SlotListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get worker
        worker = get_object_or_404(Worker, user=request.user)

        # Remove expired slots
        now = timezone.now()
        expired_slots = Slot.objects.filter(worker=worker, end_time__lt=now)
        expired_slots.delete()  # Delete expired slots from the database

        # Retrieve remaining active slots
        slots = Slot.objects.filter(worker=worker)
        serializer = SlotSerializer(slots, many=True)
        return Response({'available_slots': serializer.data}, status=200)

    def post(self, request):
        worker = get_object_or_404(Worker, user=request.user)
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")

        if end_time <= start_time:
            return Response({"error": "End time must be after start time."}, status=400)

        # Check if the slot overlaps
        overlapping_slots = Slot.objects.filter(
            worker=worker,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping_slots:
            return Response({"error": "This slot overlaps with an existing slot."}, status=400)

        slot_data = {
            "worker": worker.id,
            "start_time": start_time,
            "end_time": end_time,
            "is_available": request.data.get("is_available", True),
        }
        
        serializer = SlotSerializer(data=slot_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class SlotEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, slot_id):
        slot = get_object_or_404(Slot, id=slot_id)

        # Ensure the worker owns this slot
        if slot.worker.user != request.user:
            return Response({"error": "You are not authorized to edit this slot."}, status=403)

        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")

        if end_time <= start_time:
            return Response({"error": "End time must be after start time."}, status=400)

        # Check for overlapping slots
        overlapping_slots = Slot.objects.filter(
            worker=slot.worker,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(id=slot.id).exists()

        if overlapping_slots:
            return Response({"error": "This slot overlaps with an existing slot."}, status=400)

        # Update the slot
        slot.start_time = start_time
        slot.end_time = end_time
        slot.is_available = request.data.get("is_available", slot.is_available)
        slot.save()

        serializer = SlotSerializer(slot)
        return Response(serializer.data, status=200)

class SlotDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, slot_id):
        slot = get_object_or_404(Slot, id=slot_id)

        if slot.worker.user != request.user:
            return Response({"error": "You are not authorized to delete this slot."}, status=403)

        slot.delete()
        return Response({"message": "Slot deleted successfully."}, status=204)