from django.contrib.auth.models import AbstractUser
from django.db import models
from admin_app.models import Service

class User(AbstractUser):
    USER_ROLES = (
        ('USER', 'User'),
        ('WORKER', 'Worker'),
        ('ADMIN', 'Admin'),
    )

    email = models.EmailField(unique=True)  # Use email as the unique identifier
    role = models.CharField(max_length=10, choices=USER_ROLES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  
   

    def __str__(self):
        return self.email


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="worker_profile")
    services = models.ManyToManyField(Service, related_name="workers", blank=True)
    skills = models.TextField(blank=True, null=True)  # Can also use a ManyToManyField for predefined skills
    service_area = models.CharField(max_length=255, blank=True, null=True)
    availability_status = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    completed_jobs = models.IntegerField(default=0)

    def __str__(self):
        return f"Worker: {self.user.email}"



class Slot(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)  # If the worker is available during this slot
    is_booked = models.BooleanField(default=False) 

    class Meta:
        ordering = ['start_time']
        constraints = [
            models.UniqueConstraint(fields=['worker', 'start_time', 'end_time'], name='unique_worker_slot')
        ]


    def __str__(self):
        return f"{self.worker.user.username} - {self.start_time} to {self.end_time}"

    

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('workdone', 'Work Done'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('fee_paid', 'Fee Paid'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bookings")
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="worker_bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_bookings")
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name="slot_bookings")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return f"Booking #{self.id} - {self.user.username} with {self.worker.user.username}"


        

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.email} for {self.worker.user.email}"

