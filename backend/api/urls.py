from django.urls import path
from .views import (
    SignupView, SlotEditView, VerifyOTPView, ResendOtpAPIView,
    LoginView, ResetPasswordView, RequestPasswordResetView,
    LoginWithGoogle, UserProfileView,UserServiceListView,
    UserServiceDetailView,ServiceWorkersView,WorkerSlotPageView,
    BookingCreateView,BookingDetailView,CancelBookingView,BookingListView,
    
    WorkerSignupView, WorkerLoginView, WorkerDashboardView,
    WorkerProfileView, WorkerServicesView, WorkerServiceUpdateView,
    SlotListCreateView,SlotDeleteView
    
)

urlpatterns = [
    # User endpoints
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOtpAPIView.as_view(), name='resend_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('request-reset-password/', RequestPasswordResetView.as_view(), name='request_reset_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('login-with-google/', LoginWithGoogle.as_view(), name='login_with_google'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('services/', UserServiceListView.as_view(), name='user-service-list'), 
    path('services/<int:service_id>/', UserServiceDetailView.as_view(), name='user-service-detail'),
    path("services/<int:service_id>/workers/", ServiceWorkersView.as_view(), name="service-workers"), 
    path('worker/<int:worker_id>/slots/', WorkerSlotPageView.as_view(), name='worker-slots'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path("bookings/cancel/<int:booking_id>/", CancelBookingView.as_view(), name="cancel-booking"),
    path('user/bookings/', BookingListView.as_view(), name='user-bookings'),



    # Worker endpoints
    path('worker/signup/', WorkerSignupView.as_view(), name='worker_signup'),
    path('worker/login/', WorkerLoginView.as_view(), name='worker_login'),
    path('worker/dashboard/', WorkerDashboardView.as_view(), name='worker_dashboard'),
    path('worker/profile/', WorkerProfileView.as_view(), name='worker_profile'),
    path('worker/services/', WorkerServicesView.as_view(), name='worker-services'),
    path('worker/services/update/', WorkerServiceUpdateView.as_view(), name='worker-services-update'),
    path('worker/slots/', SlotListCreateView.as_view(), name='worker_slots'),
    path('worker/slot/edit/<int:slot_id>/', SlotEditView.as_view(), name='slot-edit'),
    path('worker/slot/delete/<int:slot_id>/', SlotDeleteView.as_view(), name='slot-delete'),
]
