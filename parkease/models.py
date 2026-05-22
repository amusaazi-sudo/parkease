from django.db import models
from django.utils import timezone

# Create your models here.

from django.contrib.auth.models import User

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ("Truck", "Truck"),
        ("Car", "Personal Car"),
        ("Taxi", "Taxi"),
        ("Coaster", "Coaster"),
        ("Boda", "Boda-boda"),
    ]
    driver_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    number_plate = models.CharField(max_length=6, unique=True)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    arrival_time = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=10)
    nin_number = models.CharField(max_length=20, blank=True, null=True)

   


class Receipt(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    
    receipt_number = models.CharField(max_length=20, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE) 
    signed_out_at = models.DateTimeField(default=timezone.now)
    amount = models.IntegerField()    
    receiver_name = models.CharField(max_length=100, blank=True, null=True)
    receiver_phone = models.CharField(max_length=10, blank=True, null=True)
    receiver_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    receiver_nin = models.CharField(max_length=20, blank=True, null=True)    
    issued_at = models.DateTimeField(auto_now_add=True)


    

   


class Report(models.Model):
    date = models.DateField()
    parking_revenue = models.IntegerField()
    tyre_revenue = models.IntegerField()
    battery_revenue = models.IntegerField()

   
class TyreService(models.Model):
    SERVICE_TYPES = [
        ("Pressure", "Pressure"),
        ("Puncture", "Puncture Fixing"),
        ("Valve", "Valve Replacement"),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    price = models.IntegerField()
    service_date = models.DateTimeField(auto_now_add=True)

    
class BatteryService(models.Model):
    SERVICE_TYPES = [
        ("Hire", "Battery Hire"),
        ("Sale", "Battery Sale"),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPES)
    price = models.IntegerField( )
    service_date = models.DateTimeField(auto_now_add=True)

    

class SystemUser(models.Model):
    ROLES = [
        ("Admin", "System Admin"),
        ("Manager", "Section Manager"),
        ("Cashier", "Cashier"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)
    name = models.CharField(max_length=20)
    email = models.EmailField(blank=False)

    