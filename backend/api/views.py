from django.http import HttpResponseBadRequest, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,views
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Booking, Review, RoomMember, User,Worker,Slot
from .serializers import (BookingSerializer, ReviewSerializer, SlotSerializer, UserSerializer,UserProfileSerializer, VisitWorkerProfileSerializer, WorkerBookingSerializer, WorkerSerializer,WorkerSignupSerializer,
                          WorkerProfileSerializer,ServiceSerializer,WorkerServiceSerializer, WorkerSlotSerializer)
from .tokens import CustomRefreshToken
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from .utils import (generate_otp, send_otp_to_email, store_otp_in_cache, 
    get_otp_from_cache,get_id_token_with_code_method_1,get_id_token_with_code_method_2)
from .serializers import RequestPasswordResetSerializer, ResetPasswordSerializer
from rest_framework import generics
from django.core.cache import cache
from django.core.mail import send_mail
from admin_app.models import Service
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from django.utils import timezone
from django.conf import settings
import paypalrestsdk
from decimal import Decimal
from agora_token_builder import RtcTokenBuilder
import json, time, random
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



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



class WorkerDetailView(APIView):
    def get(self, request, worker_id):
        try:
            worker = Worker.objects.get(id=worker_id)
            serializer = WorkerSerializer(worker)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Worker.DoesNotExist:
            return Response({"error": "Worker not found"}, status=status.HTTP_404_NOT_FOUND)

class ServiceDetailView(APIView):
    def get(self, request, service_id):
        try:
            service = Service.objects.get(id=service_id)
            serializer = ServiceSerializer(service)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

class SlotDetailView(APIView):
    def get(self, request, slot_id):
        try:
            slot = Slot.objects.get(id=slot_id)
            serializer = WorkerSlotSerializer(slot)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Slot.DoesNotExist:
            return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class WorkerReviewsView(APIView):
    def get(self, request, worker_id):
        reviews = Review.objects.filter(worker_id=worker_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlatformFeeView(APIView):
    def get(self, request):
        try:
            platform_fee = Booking._meta.get_field('platform_fee').default  # Fetch default value
            return Response({"platform_fee": platform_fee}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
paypalrestsdk.configure({
    'mode': 'sandbox',  # Change to 'live' for production
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})

class CreatePayPalOrder(APIView):
    def post(self, request):
        total_amount = request.data.get("totalAmount")
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": str(total_amount),
                    "currency": "USD"
                },
                "description": "Platform Fee Payment"
            }],
            "redirect_urls": {
                "return_url": "http://localhost:8000/payment/execute/",
                "cancel_url": "http://localhost:8000/payment/cancel/"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
            return JsonResponse({"approval_url": approval_url}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "Payment creation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecutePayPalPayment(APIView):
    def post(self, request):
        payment_id = request.data.get("paymentId")
        payer_id = request.data.get("payerId")

        # Find the PayPal payment
        payment = paypalrestsdk.Payment.find(payment_id)

        print(f"Payment found: {payment}")  # Debugging line

        # Execute the PayPal payment
        if payment.execute({"payer_id": payer_id}):
            print(f"Transaction ID after execution: {payment.id}")  # Debugging line
            
            # Fetch the worker, slot, and service objects
            worker = Worker.objects.get(id=request.data.get("worker"))
            slot = Slot.objects.get(id=request.data.get("slot"))
            service = Service.objects.get(id=request.data.get("service"))
            user = request.user

            # Default platform fee (or from the service object)
            platform_fee = getattr(service, 'platform_fee', 10)  # Default to 10 if not set
            
            # Calculate total price and remaining balance
            total_price = service.hourly_rate + platform_fee
            remaining_balance = total_price - platform_fee

            # Create a new booking object
            booking = Booking.objects.create(
                user=user,
                worker=worker,
                slot=slot,
                service=service,
                total_price=total_price,
                remaining_balance=remaining_balance,
                platform_fee=platform_fee,  
                payment_status='fee_paid',
                transaction_id=payment.id  # Storing the PayPal transaction ID
            )

            # Update slot booking status
            slot.is_booked = True
            slot.save()

            return JsonResponse({"message": "Payment and booking successful", "booking_id": booking.id}, status=status.HTTP_200_OK)
        else:
            # Debugging: Check if payment execution failed and print the error
            print(f"Payment execution failed: {payment.error}")  # Debugging line
            return JsonResponse({"error": "Payment execution failed", "details": payment.error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class BookingCreateView(APIView):
    def post(self, request):
        worker_id = request.data.get("worker")
        slot_id = request.data.get("slot")
        service_id = request.data.get("service")
        user = request.user

        if not worker_id or not slot_id or not service_id:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            worker = get_object_or_404(Worker, id=worker_id)
            slot = get_object_or_404(Slot, id=slot_id, is_booked=False)  # Ensure slot isn't already booked
            service = get_object_or_404(Service, id=service_id)

            platform_fee = Decimal(getattr(service, 'platform_fee', 10))  # Ensure platform_fee is Decimal

            # Convert duration to Decimal to avoid TypeError
            duration = Decimal((slot.end_time - slot.start_time).total_seconds()) / Decimal(3600)

            # Calculate total price correctly using Decimal
            total_price = service.hourly_rate * duration + platform_fee

            # Remaining balance should be total price minus platform fee
            remaining_balance = total_price - platform_fee

            booking = Booking.objects.create(
                user=user, 
                worker=worker, 
                slot=slot, 
                service=service,
                total_price=total_price, 
                remaining_balance=remaining_balance,
                platform_fee=platform_fee,  
                status="pending", 
                payment_status="fee_paid"
            )
            
            slot.is_available = False
            slot.save()

            return Response({
                "message": "Booking created successfully",
                "booking_id": booking.id,
                "remaining_balance": str(remaining_balance)  # Ensure JSON-safe response
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    permission_classes = [IsAuthenticated]

    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)

            # Ensure only the user who made the booking can cancel it
            if booking.user != request.user:
                return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            booking.status = "cancelled"
            # booking.payment_status = "completed" ################# error
            booking.save()

            slot = booking.slot
            slot.is_available = True
            slot.save()

            return Response(
                {"message": "Booking canceled successfully", "status": booking.status},
                status=status.HTTP_200_OK,
            )

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class UserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by("-id")
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class PayRemainingBalanceView(APIView):
    def patch(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)

            # Assuming the service price is part of the booking
            if booking.status == 'completed':
                return Response({"detail": "Booking already completed."}, status=status.HTTP_400_BAD_REQUEST)

            # Update the booking status and payment status
            booking.status = 'completed'  # or whatever status is appropriate
            booking.payment_status = 'completed'  # Assuming this field exists
            booking.save()

            return Response({"detail": "Remaining balance paid, booking is now completed."}, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        
        

class ReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        """Retrieve review for a specific booking (if exists)."""
        try:
            review = Review.objects.get(booking_id=booking_id, user=request.user)
            return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)
        except Review.DoesNotExist:
            return Response({"message": "No review found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Create a new review."""
        booking_id = request.data.get("booking_id")
        rating = request.data.get("rating")
        review_text = request.data.get("review")

        if not booking_id or not rating:
            return Response({"error": "Booking ID and rating are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user, status="completed")
            if Review.objects.filter(booking=booking).exists():
                return Response({"error": "Review already exists for this booking"}, status=status.HTTP_400_BAD_REQUEST)

            review = Review.objects.create(
                user=request.user,
                worker=booking.worker,
                booking=booking,
                rating=rating,
                review=review_text
            )
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or not completed"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, review_id):
        """Update an existing review."""
        try:
            review = Review.objects.get(id=review_id, user=request.user)
            review.rating = request.data.get("rating", review.rating)
            review.review = request.data.get("review", review.review)
            review.save()
            return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        

        
class ServiceReviewsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, service_id):
        try:
            reviews = Review.objects.filter(booking__service__id=service_id)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)


class VisitWorkerProfileView(RetrieveAPIView):
    queryset = Worker.objects.all()
    serializer_class = VisitWorkerProfileSerializer
    permission_classes = [AllowAny]
    
    
    


class GetTokenView(View):
    def get(self, request):
        app_id = "f10d6d9bb8be4f39a817074843a6a43e"
        app_certificate = "2ede2e535be8473aa063d92a14e9e499"
        channel_name = request.GET.get('channel')

        if not channel_name:
            return JsonResponse({"error": "Channel name is required"}, status=400)

        uid = random.randint(1, 230)
        expiration_time = 3600
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expiration_time
        role = 1

        token = RtcTokenBuilder.buildTokenWithUid(app_id, app_certificate, channel_name, uid, role, privilege_expired_ts)

        return JsonResponse({'token': token, 'uid': uid})


@method_decorator(csrf_exempt, name='dispatch')
class CreateMemberView(View):
    def post(self, request):
        data = json.loads(request.body)
        member, created = RoomMember.objects.get_or_create(
            name=data['name'],
            uid=data['UID'],
            room_name=data['room_name']
        )
        return JsonResponse({'name': data['name']})

class GetMemberView(View):
    def get(self, request):
        uid = request.GET.get('UID')
        room_name = request.GET.get('room_name')

        try:
            member = RoomMember.objects.get(uid=uid, room_name=room_name)
            return JsonResponse({'name': member.name})
        except RoomMember.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class DeleteMemberView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            member = RoomMember.objects.get(name=data['name'], uid=data['UID'], room_name=data['room_name'])
            member.delete()
            return JsonResponse({'message': 'Member deleted'})
        except RoomMember.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)
    


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
    
    
class WorkerBookingListView(generics.ListAPIView):
    serializer_class = WorkerBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(worker=self.request.user.worker_profile, status="pending")


class WorkerBookingUpdateView(generics.UpdateAPIView):
    serializer_class = WorkerBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk, worker=request.user.worker_profile)
            status_choice = request.data.get("status")

            if status_choice in ["processing", "cancelled"]:  
                booking.status = status_choice
                booking.save()
                return Response({"message": "Booking updated successfully", "status": booking.status})
            return Response({"error": "Invalid status choice"}, status=status.HTTP_400_BAD_REQUEST)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class WorkerManageBookingsView(generics.ListAPIView):
    serializer_class = WorkerBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(worker=self.request.user.worker_profile, status="processing")


class WorkerCompleteBookingView(generics.UpdateAPIView):
    serializer_class = WorkerBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            booking = get_object_or_404(Booking, pk=pk, worker=request.user.worker_profile, status="processing")

            # Get hours worked from request
            hours_worked = request.data.get("hours_worked")
            if hours_worked is None or float(hours_worked) <= 0:
                return Response({"error": "Invalid hours worked"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate hours worked against slot duration
            slot_duration = (booking.slot.end_time - booking.slot.start_time).total_seconds() / 3600  # Convert to hours
            if float(hours_worked) > slot_duration:
                return Response({"error": f"Hours worked cannot exceed slot duration ({slot_duration:.2f} hours)"}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total charge based on hours worked
            hourly_rate = float(booking.service.hourly_rate)  # Using 'hourly_rate' as the hourly rate
            total_price = float(hours_worked) * hourly_rate

            # Update booking details with the new total price
            booking.remaining_balance = total_price
            booking.status = "workdone"
            booking.save()

            # Mark the slot as unavailable since work is done
            if booking.slot:
                booking.slot.is_available = False
                booking.slot.save()

            return Response({
                "message": "Booking marked as completed",
                "status": booking.status,
                "remaining_balance": total_price
            })

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or not in processing status"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class WorkerReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Fetch reviews for the authenticated worker
        worker = self.request.user.worker_profile
        return Review.objects.filter(worker=worker)