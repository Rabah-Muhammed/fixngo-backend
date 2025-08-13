from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CompletedBookingsList, CreateMemberView, CreatePayPalOrder, DeleteMemberView,
    ExecutePayPalPayment, GetMemberView, GetTokenView,
    PlatformFeeView, ReviewView,ServiceDetailView, ServiceReviewsAPIView, SignupView,
    SlotDetailView, SlotEditView, UserBookingsView, VerifyOTPView, ResendOtpAPIView,
    LoginView, ResetPasswordView, RequestPasswordResetView,
    LoginWithGoogle, UserProfileView,UserServiceListView,
    UserServiceDetailView,ServiceWorkersView,
    BookingCreateView,BookingDetailView,CancelBookingView,BookingListView, 
    PayRemainingBalanceView, VisitWorkerProfileView,  WorkerReviewsView, WorkerServiceBookingsView, WorkerServiceCancelBookingsView,

    
    
    
    WorkerSignupView, WorkerLoginView, WorkerDashboardView,
    WorkerProfileView, WorkerServicesView, WorkerServiceUpdateView,
    SlotListCreateView,SlotDeleteView, WorkerBookingListView, WorkerBookingUpdateView,
    WorkerCompleteBookingView, WorkerManageBookingsView, 
    WorkerDetailView,WorkerSlotPageView,WorkerReviewListView, WorkerStartBookingView, WorkerTokenRefreshView,
    WorkerWalletView,WorkerBookingDetailView,
    
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
    path('services/<int:service_id>/workers/', ServiceWorkersView.as_view(), name='service-workers'), 
    path('worker/<int:worker_id>/slots/', WorkerSlotPageView.as_view(), name='worker-slots'),
    path('worker/<int:pk>/', VisitWorkerProfileView.as_view(), name="visit_worker_profile"),
    path('workers/<int:worker_id>/', WorkerDetailView.as_view(), name='worker-detail'),
    path('services/<int:service_id>/', ServiceDetailView.as_view(), name='service-detail'),
    path('slots/<int:slot_id>/', SlotDetailView.as_view(), name='slot-detail'),
    path('workers/<int:worker_id>/reviews/', WorkerReviewsView.as_view(), name='worker_reviews'),
    path('platform-fee/', PlatformFeeView.as_view(), name='platform-fee'),
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/cancel/<int:booking_id>/', CancelBookingView.as_view(), name='cancel-booking'),
    path('user/bookings/', BookingListView.as_view(), name='user-bookings'),
    path('api/paypal/create-order/', CreatePayPalOrder.as_view(), name='create_paypal_order'),
    path('api/paypal/execute/', ExecutePayPalPayment.as_view(), name='execute_paypal_payment'),
    path('user/bookings/', UserBookingsView.as_view(), name='user-bookings'),
    path('bookings/<int:booking_id>/pay-remaining/', PayRemainingBalanceView.as_view(), name='pay_remaining_balance'),
    path('worker-wallet/', WorkerWalletView.as_view(), name='worker-wallet'),
    path('reviews/', ReviewView.as_view(), name='create_review'),
    path('reviews/booking/<int:booking_id>/', ReviewView.as_view(), name='get_review_for_booking'),
    path('reviews/<int:review_id>/', ReviewView.as_view(), name='update_review'),
    path('services/<int:service_id>/reviews/', ServiceReviewsAPIView.as_view(), name='service-reviews'),
    path('get_token/', GetTokenView.as_view(), name="get_token"),
    path('create_member/', CreateMemberView.as_view(), name="create_member"),
    path('get_member/', GetMemberView.as_view(), name="get_member"),
    path('delete_member/', DeleteMemberView.as_view(), name="delete_member"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


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
    path('worker/bookings/', WorkerBookingListView.as_view(), name='worker-bookings'),
    path('worker/bookings/<int:pk>/', WorkerBookingUpdateView.as_view(), name='worker-booking-update'),
    path('worker/manage-bookings/', WorkerManageBookingsView.as_view(), name='worker-manage-bookings'),
    path('worker/bookings/start/<int:pk>/', WorkerStartBookingView.as_view(), name='worker-start-booking'),
    path('worker/bookings/<int:pk>/complete/', WorkerCompleteBookingView.as_view(), name='worker-complete-booking'),
    path('worker/completed-bookings/', CompletedBookingsList.as_view(), name='worker-completed-bookings'),
    path('worker/bookingdetail/<int:pk>/', WorkerBookingDetailView.as_view(), name='worker-booking-detail'),
    path('worker/reviews/', WorkerReviewListView.as_view(), name='worker-reviews'),
    path('worker/dashboard/', WorkerDashboardView.as_view(), name='worker-dashboard'),
    path('worker/services/<int:service_id>/bookings/', WorkerServiceBookingsView.as_view(), name='worker-service-bookings'),
    path('worker/services/<int:service_id>/cancel-bookings/', WorkerServiceCancelBookingsView.as_view(), name='worker-service-cancel-bookings'),
    path('worker/token/refresh/', WorkerTokenRefreshView.as_view(), name='worker_token_refresh'),
    
]
   
    
