from django import forms
from .models import Vehicle, SignOut, TyreService, BatteryService, TyrePriceSetting, BatteryPriceSetting
from .utils import validate_ugandan_phone, validate_nin, validate_number_plate

class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['driver_name', 'vehicle_type', 'number_plate', 'vehicle_model', 
                  'color', 'phone_number', 'nin_number']
        widgets = {
            'arrival_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_driver_name(self):
        name = self.cleaned_data.get('driver_name')
        if not name[0].isupper():
            raise forms.ValidationError("Name must start with a capital letter.")
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Name cannot contain numbers.")
        return name

    def clean_number_plate(self):
        plate = self.cleaned_data.get('number_plate')
        if not validate_number_plate(plate):
            raise forms.ValidationError("Number plate must start with 'U' and be alphanumeric (max 6 chars).")
        return plate.upper()

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not validate_ugandan_phone(phone):
            raise forms.ValidationError("Invalid Ugandan phone number.")
        return phone

    def clean_nin_number(self):
        nin = self.cleaned_data.get('nin_number')
        if nin and not validate_nin(nin):
            raise forms.ValidationError("Invalid NIN format.")
        return nin

    def clean(self):
        cleaned_data = super().clean()
        vehicle_type = cleaned_data.get('vehicle_type')
        nin = cleaned_data.get('nin_number')
        if vehicle_type == 'BODA' and not nin:
            self.add_error('nin_number', 'NIN is required for Boda-boda.')
        return cleaned_data

class SignOutForm(forms.ModelForm):
    class Meta:
        model = SignOut
        fields = ['receiver_name', 'phone_number', 'gender', 'nin_number']

    def clean_receiver_name(self):
        name = self.cleaned_data.get('receiver_name')
        if name and name[0].islower():
            name = name.capitalize()
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Name cannot contain numbers.")
        return name

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not validate_ugandan_phone(phone):
            raise forms.ValidationError("Invalid Ugandan phone number.")
        return phone

    def clean_nin_number(self):
        nin = self.cleaned_data.get('nin_number')
        if nin and not validate_nin(nin):
            raise forms.ValidationError("Invalid NIN format.")
        return nin

class TyreServiceForm(forms.ModelForm):
    class Meta:
        model = TyreService
        fields = ['customer_name', 'tyre_size', 'tyre_model', 'service_type']

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name')
        if name and not name[0].isupper():
            name = name.capitalize()
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Name cannot contain numbers.")
        return name

class BatteryServiceForm(forms.ModelForm):
    class Meta:
        model = BatteryService
        fields = ['customer_name', 'battery_type', 'service_type']

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name')
        if name and not name[0].isupper():
            name = name.capitalize()
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Name cannot contain numbers.")
        return name

class TyrePriceSettingForm(forms.ModelForm):
    class Meta:
        model = TyrePriceSetting
        fields = ['service_type', 'price']
        widgets = {
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price in UGX',
                'min': '0',
                'step': '100'
            }),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        if price and price > 1000000:
            raise forms.ValidationError("Price seems unusually high. Please verify.")
        return price

class BatteryPriceSettingForm(forms.ModelForm):
    class Meta:
        model = BatteryPriceSetting
        fields = ['battery_type', 'hire_price', 'sale_price']
        widgets = {
            'battery_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 100Ah, 200Ah'
            }),
            'hire_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hire price in UGX',
                'min': '0',
                'step': '100'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sale price in UGX',
                'min': '0',
                'step': '100'
            }),
        }

    def clean_hire_price(self):
        price = self.cleaned_data.get('hire_price')
        if price and price < 0:
            raise forms.ValidationError("Hire price cannot be negative.")
        return price

    def clean_sale_price(self):
        price = self.cleaned_data.get('sale_price')
        if price and price < 0:
            raise forms.ValidationError("Sale price cannot be negative.")
        return price