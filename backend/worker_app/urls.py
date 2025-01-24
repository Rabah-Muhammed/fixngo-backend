# worker_app/urls.py
from django.urls import path
from .views import WorkerSignupView, WorkerLoginView,WorkerDashboardView,WorkerProfileView,ServiceListView,ServiceCreateView

urlpatterns = [
    path('signup/', WorkerSignupView.as_view(), name='worker_signup'),
    path('login/', WorkerLoginView.as_view(), name='worker_login'),
    path('dashboard/', WorkerDashboardView.as_view(), name='worker_dashboard'), 
    path('profile/', WorkerProfileView.as_view(), name='worker_profile'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('service/create/', ServiceCreateView.as_view(), name='service-create'),
]
