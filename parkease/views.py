# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Vehicle, Receipt
import uuid
from datetime import datetime

@login_required
def register_vehicle(request):
    """Register a new vehicle"""
    if request.method == 'POST':
        # Get form data
        driver_name = request.POST.get('driver_name')
        vehicle_type = request.POST.get('vehicle_type')
        number_plate = request.POST.get('number_plate').upper()
        model = request.POST.get('vehicle_brand')
        color = request.POST.get('color')
        phone_number = request.POST.get('phone_number')
        nin_number = request.POST.get('nin_number')
        
        # Create vehicle
        vehicle = Vehicle.objects.create(
            driver_name=driver_name,
            vehicle_type=vehicle_type,
            number_plate=number_plate,
            model=model,
            color=color,
            phone_number=phone_number,
            nin_number=nin_number
        )
        
        return redirect('register_table')
    
    return render(request, 'parking_attendant/register.html')

@login_required
def register_table(request):
   
    vehicles = Vehicle.objects.all().order_by('-id')
    return render(request, 'parking_attendant/register_table.html', {'vehicles': vehicles})

@login_required
def sign_out(request):
    if request.method == 'POST':
        number_plate = request.POST.get('number_plate').upper()   
       
        receiver_name = request.POST.get('receiver_name')
        receiver_phone = request.POST.get('receiver_phone')
        receiver_gender = request.POST.get('receiver_gender')
        receiver_nin = request.POST.get('receiver_nin')
        
        vehicle = Vehicle.objects.filter(number_plate=number_plate).first()
        
        if not vehicle:
            vehicles = Vehicle.objects.all().order_by('-arrival_time')
            return render(request, 'parking_attendant/sign_out.html', {
                'vehicles': vehicles,
                'error': 'Vehicle not found! Please register first.'
            })
        
        # Calculate charges (existing code)
        now = timezone.now()
        duration_hours = (now - vehicle.arrival_time).total_seconds() / 3600
        is_night = now.hour >= 19 or now.hour < 6
        amount = calculate_parking_fee(vehicle.vehicle_type, duration_hours, is_night)
        
        # Create receipt with new fields
        receipt = Receipt.objects.create(
            receipt_number=f"RCP-{uuid.uuid4().hex[:8].upper()}",
            vehicle=vehicle,
            signed_out_at=now,
            amount=amount,
            # NEW FIELDS
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_gender=receiver_gender,
            receiver_nin=receiver_nin,
        )
        
        return redirect('receipt', receipt_id=receipt.id)
    
    vehicles = Vehicle.objects.all().order_by('-arrival_time')
    return render(request, 'parking_attendant/sign_out.html', {'vehicles': vehicles})
def calculate_parking_fee(vehicle_type, duration_hours, is_night):
    """Calculate parking fee based on vehicle type and duration"""
    
    if vehicle_type == 'Truck':
        if duration_hours < 3:
            return 2000
        elif is_night:
            return 10000
        else:
            return 5000
    
    elif vehicle_type == 'Car':
        if duration_hours < 3:
            return 2000
        elif is_night:
            return 2000
        else:
            return 3000
    
    elif vehicle_type == 'Taxi':
        if duration_hours < 3:
            return 2000
        elif is_night:
            return 2000
        else:
            return 3000
    
    elif vehicle_type == 'Coaster':
        if duration_hours < 3:
            return 3000
        elif is_night:
            return 2000
        else:
            return 4000
    
    else:  # Boda
        if duration_hours < 3:
            return 1000
        else:
            return 2000

@login_required
def receipt_view(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id)
    
    # Calculate everything here
    duration = receipt.signed_out_at - receipt.vehicle.arrival_time
    duration_hours = duration.total_seconds() / 3600
    is_night = receipt.signed_out_at.hour >= 19 or receipt.signed_out_at.hour < 6
    time_period = 'Night' if is_night else 'Day'
    vt = receipt.vehicle.vehicle_type
    
    # Simple charge breakdown
    if vt == 'Truck':
        if duration_hours < 3:
            charge = "Truck - Short stay: UGX 2,000"
        elif is_night:
            charge = "Truck - Night rate: UGX 10,000"
        else:
            charge = "Truck - Day rate: UGX 5,000"
    elif vt in ['Car', 'Taxi']:
        if duration_hours < 3 or is_night:
            charge = f"{vt} - UGX 2,000"
        else:
            charge = f"{vt} - Day rate: UGX 3,000"
    elif vt == 'Coaster':
        if duration_hours < 3:
            charge = "Coaster - Short stay: UGX 3,000"
        elif is_night:
            charge = "Coaster - Night rate: UGX 2,000"
        else:
            charge = "Coaster - Day rate: UGX 4,000"
    else:
        charge = "Boda-boda - UGX 1,000" if duration_hours < 3 else "Boda-boda - UGX 2,000"
    
    context = {
        'receipt': receipt,
        'vehicle': receipt.vehicle,
        'duration_hours': round(duration_hours, 2),
        'time_period': time_period,
        'charge_breakdown': charge,
        'issued_at': receipt.issued_at,
        'signed_out_at': receipt.signed_out_at,
    }
    
    return render(request, 'parking_attendant/receipt.html', context)