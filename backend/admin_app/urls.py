# admin_app/urls.py
from django.urls import path
from .views import (AdminLoginView,AdminDashboardView, BookingListView, CancelBookingView, ServiceUpdateView,UsersListView,BlockUserView,
                    UnblockUserView,DeleteUserView,WorkersListView,BlockWorkerView,
                    UnblockWorkerView,DeleteWorkerView,ServiceListCreateView,
                    ServiceDeleteView)

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin-login'),  # Admin login endpoint
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),  # Protect this endpoint
    path('users/', UsersListView.as_view(), name='users_list'),  # Add this path
    path('block/<int:user_id>/', BlockUserView.as_view(), name='block-user'),
    path('unblock/<int:user_id>/', UnblockUserView.as_view(), name='unblock-user'),
    path("delete/<int:user_id>/", DeleteUserView.as_view(), name="delete-user"),
    path('workers/', WorkersListView.as_view(), name='workers-list'),
    path("block/<int:worker_id>/", BlockWorkerView.as_view(), name="block-worker"),
    path("unblock/<int:worker_id>/", UnblockWorkerView.as_view(), name="unblock-worker"),
    path("delete/<int:worker_id>/", DeleteWorkerView.as_view(), name="delete-worker"),
    path('services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<int:pk>/', ServiceUpdateView.as_view(), name='service-update'),
    path('services/<int:pk>/', ServiceDeleteView.as_view(), name='service-delete'),
 
]
   

