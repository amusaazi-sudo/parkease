from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.models import User

class Vehicle(models.Model):
    VEHICLE_CHOICES = [
        ('TRUCK', 'Truck'),
        ('PERSONAL', 'Personal Car'),
        ('TAXI', 'Taxi'),
        ('COASTER', 'Coaster'),
        ('BODA', 'Boda-boda'),
    ]
    driver_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    number_plate = models.CharField(max_length=10, unique=True)
    vehicle_model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    arrival_datetime = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15)
    nin_number = models.CharField(max_length=20, blank=True, null=True)
    is_signed_out = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.number_plate} - {self.driver_name}"

class ParkingReceipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=0)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField()
    duration = models.DecimalField(max_digits=5, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='PAID')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"PRK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class SignOut(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    receiver_name = models.CharField(max_length=100)
    receipt_number = models.CharField(max_length=50)
    signout_datetime = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nin_number = models.CharField(max_length=20, blank=True)

class TyreService(models.Model):
    SERVICE_CHOICES = [
        ('PRESSURE', 'Pressure Check'),
        ('PUNCTURE', 'Puncture Fixing'),
        ('VALVE', 'Valve Replacement'),
    ]
    customer_name = models.CharField(max_length=100)
    tyre_size = models.CharField(max_length=20)
    tyre_model = models.CharField(max_length=50)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    service_price = models.DecimalField(max_digits=10, decimal_places=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class TyrePriceSetting(models.Model):
    SERVICE_CHOICES = [
        ('PRESSURE', 'Pressure Check'),
        ('PUNCTURE', 'Puncture Fixing'),
        ('VALVE', 'Valve Replacement'),
    ]
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)

class BatteryService(models.Model):
    SERVICE_CHOICES = [('HIRE', 'Hire'), ('SALE', 'Sale')]
    customer_name = models.CharField(max_length=100)
    battery_type = models.CharField(max_length=50)
    service_type = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class BatteryPriceSetting(models.Model):
    battery_type = models.CharField(max_length=50, unique=True)
    hire_price = models.DecimalField(max_digits=10, decimal_places=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=0)

