import re
from datetime import datetime

def calculate_parking_fee(vehicle_type, entry_datetime, exit_datetime):
    duration = exit_datetime - entry_datetime
    hours = duration.total_seconds() / 3600

    rates = {
        'TRUCK': {'day': 5000, 'night': 10000, 'short': 2000},
        'PERSONAL': {'day': 3000, 'night': 2000, 'short': 2000},
        'TAXI': {'day': 3000, 'night': 2000, 'short': 2000},
        'COASTER': {'day': 4000, 'night': 2000, 'short': 3000},
        'BODA': {'day': 2000, 'night': 2000, 'short': 1000},
    }
    vehicle_rates = rates.get(vehicle_type, rates['PERSONAL'])
    if hours <= 3:
        return vehicle_rates['short']
    arrival_hour = entry_datetime.hour
    if 6 <= arrival_hour < 19:
        return vehicle_rates['day']
    else:
        return vehicle_rates['night']

def validate_ugandan_phone(phone):
    pattern = r'^(256|0)?(7[0-9]{8}|2[0-9]{8}|3[0-9]{8}|4[0-9]{8})$'
    return bool(re.match(pattern, phone))

def validate_nin(nin):
    pattern = r'^[A-Z]{2}[0-9]{8}[A-Z]{2}[0-9]$'
    return bool(re.match(pattern, nin))

def validate_number_plate(plate):
    pattern = r'^U[A-Z0-9]{1,5}$'
    return bool(re.match(pattern, plate.upper()))