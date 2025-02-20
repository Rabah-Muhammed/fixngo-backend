from django.contrib import admin
from .models import User,Worker,Slot,Booking,Review,RoomMember

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'username')
    
@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_area', 'availability_status', 'rating', 'completed_jobs')
    search_fields = ('user__email', 'service_area')


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('worker', 'start_time', 'end_time', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('worker__user__email', 'start_time', 'end_time')


admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(RoomMember)