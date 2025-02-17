from django.db import models

# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='service_images/', null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name