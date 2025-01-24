# worker_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import WorkerSignupSerializer,WorkerProfileSerializer,ServiceSerializer
from api.models import Worker
from django.contrib.auth import authenticate
from .tokens import CustomRefreshToken
from api.models import User
from .models import Service
from rest_framework.permissions import IsAuthenticated


class WorkerSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WorkerSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Create the user
            Worker.objects.create(user=user)  # Create associated worker profile
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
        
    
class ServiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure the worker is associated with the User model
        worker = Worker.objects.get(user=request.user)
        services = Service.objects.filter(worker=worker)
        serializer = ServiceSerializer(services, many=True)
        return Response({"services": serializer.data}, status=status.HTTP_200_OK)

class ServiceCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the Worker instance from the User
        try:
            # Assuming each User has a related Worker profile
            worker = Worker.objects.get(user=request.user)
        except Worker.DoesNotExist:
            return Response({"error": "Worker profile not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Now, save the service with the correct worker instance
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(worker=worker)  # Pass the Worker instance here
            return Response({"message": "Service created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)