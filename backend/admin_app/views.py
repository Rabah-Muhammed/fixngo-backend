# backend/admin_app/views.py
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .tokens import CustomRefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.models import Booking, Review, User, Worker
from .serializers import BookingDetailSerializer, BookingSerializer, ReviewSerializer, ServiceSerializer
from .models import Service
from django.db.models.functions import TruncMonth
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count,Sum


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        # Authenticate the admin user
        user = authenticate(email=email, password=password)

        if user:
            if user.is_superuser:  # Check if the user is superuser
                # Generate custom JWT token including is_superuser as a claim
                refresh = CustomRefreshToken.for_user(user)  # Correct method call
                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "role": "ADMIN",  # Add role as "ADMIN"
                        "is_superuser": user.is_superuser,  # Include superuser status
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "You are not authorized as an admin."}, status=status.HTTP_403_FORBIDDEN)

        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    
    
    
class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_workers = Worker.objects.count()
        active_workers = Worker.objects.filter(user__is_active=True).count()
        total_services = Service.objects.count()
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status="pending").count()
        completed_bookings = Booking.objects.filter(status="completed").count()
        cancelled_bookings = Booking.objects.filter(status="cancelled").count()
        platform_earnings = Booking.objects.aggregate(total=Sum('platform_fee'))['total'] or Decimal("0")
        total_earnings = Booking.objects.filter(status="completed").aggregate(total=Sum('remaining_balance'))['total'] or Decimal("0")

        total_earnings = total_earnings + platform_earnings



        # Monthly booking trend
        monthly_bookings = (
            Booking.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        booking_trend_data = {entry["month"].strftime('%Y-%m'): entry["count"] for entry in monthly_bookings}

        recent_bookings = Booking.objects.select_related('user', 'worker', 'service').order_by('-created_at')[:5]
        recent_bookings_data = [
            {
                "id": booking.id,
                "user": booking.user.username if booking.user else "N/A",
                "worker": booking.worker.user.username if booking.worker else "N/A",
                "service": booking.service.name if booking.service else "N/A",
                "status": booking.status,
                "amount": booking.remaining_balance,
                "created_at": booking.created_at,
            }
            for booking in recent_bookings
        ]

        return Response({
            "total_users": total_users,
            "active_users": active_users,
            "total_workers": total_workers,
            "active_workers": active_workers,
            "total_services": total_services,
            "total_bookings": total_bookings,
            "pending_bookings": pending_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_earnings": total_earnings,
            "platform_earnings": platform_earnings, 
            "booking_trend_data": booking_trend_data,
            "recent_bookings": recent_bookings_data,
        })

    
class UsersListView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated admins can access
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Fetch all users except admins
        users = User.objects.filter(role='USER')  # Adjust to your role filtering logic
        
        users_data = []
        
        for user in users:
            users_data.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
            })
        
        return Response(users_data)
    
class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = False  # Block the user
        user.save()
        return Response({"message": "User blocked successfully."}, status=status.HTTP_200_OK)


class UnblockUserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True  # Unblock the user
        user.save()
        return Response({"message": "User unblocked successfully."}, status=status.HTTP_200_OK)
    

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role="USER")  # Ensure the user is not a worker/admin
            user.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


    
class WorkersListView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated admins can access
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Fetch all workers
        workers = User.objects.filter(role='WORKER')  # Filter workers based on role
        workers_data = []

        for worker in workers:
            workers_data.append({
                "id": worker.id,
                "email": worker.email,
                "username": worker.username,
                "phone_number": worker.phone_number,
                "is_active": worker.is_active,
                "date_joined": worker.date_joined,
            })

        return Response(workers_data)
    
class BlockWorkerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, worker_id):
        try:
            worker = User.objects.get(id=worker_id, role="WORKER")
            worker.is_active = False  # Set the worker's status to inactive
            worker.save()
            return Response({"message": f"Worker {worker.username} has been blocked."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Worker not found or invalid role."}, status=status.HTTP_404_NOT_FOUND)


class UnblockWorkerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, worker_id):
        try:
            worker = User.objects.get(id=worker_id, role="WORKER")
            worker.is_active = True  # Set the worker's status to active
            worker.save()
            return Response({"message": f"Worker {worker.username} has been unblocked."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Worker not found or invalid role."}, status=status.HTTP_404_NOT_FOUND)
        

class DeleteWorkerView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, worker_id):
        try:
            worker = User.objects.get(id=worker_id, role="WORKER")
            worker.delete()
            return Response({"message": f"Worker {worker.username} has been deleted."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Worker not found or invalid role."}, status=status.HTTP_404_NOT_FOUND)


class ServiceListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        services = Service.objects.all().order_by('-created_at')
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            service = Service.objects.get(pk=pk)
            serializer = ServiceSerializer(service, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            service = Service.objects.get(pk=pk)
            service.delete()
            return Response({"message": "Service deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Service.DoesNotExist:
            return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
        
        

class AdminBookingListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
class AdminBookingDetail(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, booking_id):
        try:
            # Fetch the booking with related user, worker, and service
            booking = Booking.objects.select_related("user", "worker", "service").get(id=booking_id)
            # Serialize the booking data
            serializer = BookingDetailSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, booking_id):
        try:
            # Get the booking by ID
            booking = Booking.objects.get(id=booking_id)
            
            # Check if the status is 'pending'
            if booking.status != 'pending':
                return Response(
                    {"error": "Only pending bookings can be cancelled."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Change the booking status to 'cancelled'
            booking.status = 'cancelled'
            booking.save()

            return Response(
                {"message": "Booking cancelled successfully."},
                status=status.HTTP_200_OK
            )

        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        
class ReviewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            reviews = Review.objects.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)