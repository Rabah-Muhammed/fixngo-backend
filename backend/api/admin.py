from django.contrib import admin
from .models import User,Worker
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'username')
    
@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_area', 'availability_status', 'rating', 'completed_jobs')
    search_fields = ('user__email', 'service_area')

