from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import Vehicle, ParkingReceipt, SignOut, TyreService, TyrePriceSetting, BatteryService, BatteryPriceSetting
from .forms import VehicleRegistrationForm, SignOutForm, TyreServiceForm, BatteryServiceForm
from .utils import calculate_parking_fee
from .decorators import group_required

# Authentication
def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome {user.username}')
            return redirect('core:dashboard_redirect')
        messages.error(request, 'Invalid credentials')
    return render(request, 'web1/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:login')

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_superuser:
        return redirect('core:admin_dashboard')
    groups = user.groups.all()
    if groups.exists():
        group = groups[0].name
        if group == 'System Admin':
            return redirect('core:admin_dashboard')
        elif group == 'Parking Attendant':
            return redirect('core:parking_dashboard')
        elif group == 'Section Manager':
            return redirect('core:manager_dashboard')
    return redirect('core:parking_dashboard')

# Admin dashboard
@login_required
@group_required('System Admin')
def admin_dashboard(request):
    today = timezone.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    vehicles_today = Vehicle.objects.filter(arrival_datetime__date=today).count()
    signed_out_today = SignOut.objects.filter(signout_datetime__date=today).count()
    parking_revenue = ParkingReceipt.objects.filter(exit_time__date=today).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    tyre_revenue = TyreService.objects.filter(created_at__date=today).aggregate(Sum('service_price'))['service_price__sum'] or 0
    battery_revenue = BatteryService.objects.filter(created_at__date=today).aggregate(Sum('price'))['price__sum'] or 0
    total_revenue = parking_revenue + tyre_revenue + battery_revenue

    # Last 7 days revenue for simple bar (CSS)
    last_7_days = []
    parking_7d = []
    tyre_7d = []
    battery_7d = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        last_7_days.append(day.strftime('%Y-%m-%d'))
        parking_7d.append(ParkingReceipt.objects.filter(exit_time__date=day).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0)
        tyre_7d.append(TyreService.objects.filter(created_at__date=day).aggregate(Sum('service_price'))['service_price__sum'] or 0)
        battery_7d.append(BatteryService.objects.filter(created_at__date=day).aggregate(Sum('price'))['price__sum'] or 0)
    max_rev = max(parking_7d + tyre_7d + battery_7d) or 1

    context = {
        'vehicles_today': vehicles_today,
        'signed_out_today': signed_out_today,
        'parking_revenue': parking_revenue,
        'tyre_revenue': tyre_revenue,
        'battery_revenue': battery_revenue,
        'total_revenue': total_revenue,
        'last_7_days': last_7_days,
        'parking_7d': parking_7d,
        'tyre_7d': tyre_7d,
        'battery_7d': battery_7d,
        'max_rev': max_rev,
    }
    return render(request, 'web1/admin_dashboard.html', context)

# Parking attendant views
@login_required
@group_required('Parking Attendant', 'System Admin')
def parking_dashboard(request):
    active_count = Vehicle.objects.filter(is_signed_out=False).count()
    today_count = Vehicle.objects.filter(arrival_datetime__date=timezone.now().date()).count()
    recent_vehicles = Vehicle.objects.all().order_by('-arrival_datetime')[:10]
    return render(request, 'web1/parking_dashboard.html', {
        'active_count': active_count,
        'today_count': today_count,
        'recent_vehicles': recent_vehicles
    })

@login_required
@group_required('Parking Attendant', 'System Admin')
def register_vehicle(request):
    if request.method == 'POST':
        form = VehicleRegistrationForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.created_by = request.user
            vehicle.save()
            messages.success(request, f'Vehicle {vehicle.number_plate} registered')
            return redirect('core:active_vehicles')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = VehicleRegistrationForm()
    return render(request, 'web1/register_vehicle.html', {'form': form})

@login_required
@group_required('Parking Attendant', 'System Admin')
def active_vehicles(request):
    vehicles = Vehicle.objects.filter(is_signed_out=False).order_by('-arrival_datetime')
    return render(request, 'web1/active_vehicles.html', {'vehicles': vehicles})

@login_required
@group_required('Parking Attendant', 'System Admin')
def signout_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, is_signed_out=False)
    if request.method == 'POST':
        form = SignOutForm(request.POST)
        if form.is_valid():
            exit_time = timezone.now()
            fee = calculate_parking_fee(vehicle.vehicle_type, vehicle.arrival_datetime, exit_time)
            duration = (exit_time - vehicle.arrival_datetime).total_seconds() / 3600
            receipt = ParkingReceipt.objects.create(
                vehicle=vehicle, amount_paid=fee, entry_time=vehicle.arrival_datetime,
                exit_time=exit_time, duration=round(duration, 2)
            )
            signout = form.save(commit=False)
            signout.vehicle = vehicle
            signout.receipt_number = receipt.receipt_number
            signout.save()
            vehicle.is_signed_out = True
            vehicle.save()
            messages.success(request, f'Signed out {vehicle.number_plate}. Amount: UGX {fee}')
            return redirect('core:receipt', receipt_id=receipt.id)
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SignOutForm()
    return render(request, 'web1/signout_vehicle.html', {'vehicle': vehicle, 'form': form})

@login_required
def receipt(request, receipt_id):
    receipt = get_object_or_404(ParkingReceipt, id=receipt_id)
    signout = SignOut.objects.filter(receipt_number=receipt.receipt_number).first()
    return render(request, 'web1/receipt.html', {'receipt': receipt, 'signout': signout, 'vehicle': receipt.vehicle})

# Tyre clinic views
@login_required
@group_required('Section Manager', 'System Admin')
def manager_dashboard(request):
    today = timezone.now().date()
    tyre_count = TyreService.objects.filter(created_at__date=today).count()
    battery_count = BatteryService.objects.filter(created_at__date=today).count()
    tyre_revenue = TyreService.objects.filter(created_at__date=today).aggregate(Sum('service_price'))['service_price__sum'] or 0
    battery_revenue = BatteryService.objects.filter(created_at__date=today).aggregate(Sum('price'))['price__sum'] or 0
    return render(request, 'web1/manager_dashboard.html', {
        'tyre_count': tyre_count, 'battery_count': battery_count,
        'tyre_revenue': tyre_revenue, 'battery_revenue': battery_revenue
    })

@login_required
@group_required('Section Manager', 'System Admin')
def tyre_service(request):
    if request.method == 'POST':
        form = TyreServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            # Get price from price settings
            price_setting = TyrePriceSetting.objects.filter(service_type=service.service_type).first()
            if price_setting:
                service.service_price = price_setting.price
            else:
                service.service_price = 500  # fallback
            service.created_by = request.user
            service.save()
            messages.success(request, f'Tyre service recorded: {service.get_service_type_display()} - UGX {service.service_price}')
            return redirect('core:tyre_transactions')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = TyreServiceForm()
    prices = {p.service_type: p.price for p in TyrePriceSetting.objects.all()}
    return render(request, 'web1/tyre_service.html', {'form': form, 'prices': prices})

@login_required
@group_required('Section Manager', 'System Admin')
def tyre_transactions(request):
    transactions = TyreService.objects.all().order_by('-created_at')
    total = sum(t.service_price for t in transactions)
    return render(request, 'web1/tyre_transactions.html', {'transactions': transactions, 'total_revenue': total})

@login_required
@group_required('Section Manager', 'System Admin')
def manage_tyre_prices(request):
    if request.method == 'POST':
        for service in ['PRESSURE', 'PUNCTURE', 'VALVE']:
            price = request.POST.get(f'price_{service}')
            if price:
                setting, _ = TyrePriceSetting.objects.get_or_create(service_type=service)
                setting.price = price
                setting.save()
        messages.success(request, 'Tyre prices updated')
        return redirect('core:manage_tyre_prices')

    service_names = {
        'PRESSURE': 'Pressure Check',
        'PUNCTURE': 'Puncture Fixing',
        'VALVE': 'Valve Replacement'
    }
    tyre_services = []
    for service in ['PRESSURE', 'PUNCTURE', 'VALVE']:
        setting = TyrePriceSetting.objects.filter(service_type=service).first()
        tyre_services.append({
            'service': service,
            'name': service_names[service],
            'price': setting.price if setting else (500 if service == 'PRESSURE' else 5000),
        })

    return render(request, 'web1/manage_tyre_prices.html', {'tyre_services': tyre_services})

# Battery views
@login_required
@group_required('Section Manager', 'System Admin')
def battery_service(request):
    if request.method == 'POST':
        form = BatteryServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            # Get price from settings
            price_setting = BatteryPriceSetting.objects.filter(battery_type=service.battery_type).first()
            if price_setting:
                if service.service_type == 'HIRE':
                    service.price = price_setting.hire_price
                else:
                    service.price = price_setting.sale_price
            else:
                service.price = 0
            service.created_by = request.user
            service.save()
            messages.success(request, f'Battery {service.service_type} recorded: UGX {service.price}')
            return redirect('core:battery_transactions')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = BatteryServiceForm()
    return render(request, 'web1/battery_services.html', {'form': form})

@login_required
@group_required('Section Manager', 'System Admin')
def battery_transactions(request):
    transactions = BatteryService.objects.all().order_by('-created_at')
    total = sum(t.price for t in transactions)
    return render(request, 'web1/battery_transactions.html', {'transactions': transactions, 'total_revenue': total})

@login_required
@group_required('Section Manager', 'System Admin')
def manage_battery_prices(request):
    if request.method == 'POST':
        battery_types = request.POST.getlist('battery_type[]')
        hire_prices = request.POST.getlist('hire_price[]')
        sale_prices = request.POST.getlist('sale_price[]')
        for i, bt in enumerate(battery_types):
            if bt:
                setting, _ = BatteryPriceSetting.objects.get_or_create(battery_type=bt)
                setting.hire_price = hire_prices[i]
                setting.sale_price = sale_prices[i]
                setting.save()
        new_type = request.POST.get('new_battery_type')
        new_hire = request.POST.get('new_hire_price')
        new_sale = request.POST.get('new_sale_price')
        if new_type and new_hire and new_sale:
            BatteryPriceSetting.objects.create(battery_type=new_type, hire_price=new_hire, sale_price=new_sale)
        messages.success(request, 'Battery prices updated')
        return redirect('core:manage_battery_prices')
    settings = BatteryPriceSetting.objects.all()
    return render(request, 'web1/manage_battery_prices.html', {'settings': settings})

# Reporting
@login_required
@group_required('System Admin')
def daily_report(request):
    report_date = request.GET.get('date', timezone.now().date())
    if isinstance(report_date, str):
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    parking = ParkingReceipt.objects.filter(exit_time__date=report_date)
    parking_total = parking.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    tyre = TyreService.objects.filter(created_at__date=report_date)
    tyre_total = tyre.aggregate(Sum('service_price'))['service_price__sum'] or 0
    battery = BatteryService.objects.filter(created_at__date=report_date)
    battery_total = battery.aggregate(Sum('price'))['price__sum'] or 0
    signed_out = SignOut.objects.filter(signout_datetime__date=report_date)
    context = {
        'report_date': report_date,
        'parking_transactions': parking,
        'parking_total': parking_total,
        'tyre_transactions': tyre,
        'tyre_total': tyre_total,
        'battery_transactions': battery,
        'battery_total': battery_total,
        'signed_out': signed_out,
        'grand_total': parking_total + tyre_total + battery_total,
    }
    return render(request, 'web1/daily_report.html', context)
