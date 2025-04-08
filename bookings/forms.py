from django import forms
from django.forms import formset_factory, modelformset_factory
from .models import Booking
from .models_driver import Driver
import datetime

class BookingForm(forms.ModelForm):
    """
    Form for creating a booking
    """
    class Meta:
        model = Booking
        fields = ['pickup_location', 'dropoff_location', 'pickup_date', 'return_date', 'driver_age']
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'driver_age': forms.NumberInput(attrs={'min': 18, 'max': 99}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        pickup_date = cleaned_data.get('pickup_date')
        return_date = cleaned_data.get('return_date')
        driver_age = cleaned_data.get('driver_age')
        
        # Validate pickup date is not in the past
        if pickup_date and pickup_date < datetime.date.today():
            self.add_error('pickup_date', 'Pickup date cannot be in the past')
        
        # Validate return date is after pickup date
        if pickup_date and return_date and return_date < pickup_date:
            self.add_error('return_date', 'Return date must be after pickup date')
        
        # Validate driver age
        if driver_age and (driver_age < 18 or driver_age > 99):
            self.add_error('driver_age', 'Driver must be between 18 and 99 years old')
        
        return cleaned_data

class DriverForm(forms.ModelForm):
    """
    Form for adding driver information
    """
    # 添加国家选项，设置默认为澳大利亚
    COUNTRY_CHOICES = [
        ('Australia', 'Australia'),
        ('New Zealand', 'New Zealand'),
        ('United States', 'United States'),
        ('United Kingdom', 'United Kingdom'),
        ('China', 'China'),
        ('Japan', 'Japan'),
        ('Singapore', 'Singapore'),
        ('Malaysia', 'Malaysia'),
        ('Indonesia', 'Indonesia'),
        ('Thailand', 'Thailand'),
        ('Vietnam', 'Vietnam'),
        ('South Korea', 'South Korea'),
        ('India', 'India'),
        ('Germany', 'Germany'),
        ('France', 'France'),
        ('Italy', 'Italy'),
        ('Spain', 'Spain'),
        ('Canada', 'Canada'),
        ('Brazil', 'Brazil'),
        ('South Africa', 'South Africa'),
        ('Other', 'Other'),
    ]
    
    # 覆盖国家字段，使用选择列表
    country_of_residence = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        initial='Australia',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Driver
        fields = [
            'first_name', 'last_name', 'email', 'date_of_birth',
            'license_number', 'license_issued_in', 'license_expiry_date', 'license_is_lifetime',
            'address', 'local_address', 'city', 'state', 'postcode', 'country_of_residence',
            'phone', 'mobile', 'fax', 'occupation', 'mailing_list', 'is_primary'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'license_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'local_address': forms.TextInput(attrs={'placeholder': 'Optional'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Optional'}),
            'fax': forms.TextInput(attrs={'placeholder': 'Optional'}),
            'occupation': forms.Select(attrs={'class': 'form-select'}),
            'mailing_list': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = datetime.date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 18:
                raise forms.ValidationError("Driver must be at least 18 years old")
            if age > 99:
                raise forms.ValidationError("Driver age cannot exceed 99 years")
        return date_of_birth
    
    def clean_license_expiry_date(self):
        expiry_date = self.cleaned_data.get('license_expiry_date')
        is_lifetime = self.cleaned_data.get('license_is_lifetime')
        
        if not is_lifetime and expiry_date:
            if expiry_date < datetime.date.today():
                raise forms.ValidationError("License has expired")
        
        return expiry_date

class CancellationForm(forms.Form):
    """
    Form for cancelling a booking
    """
    REASONS = [
        ('', '-- Select Reason --'),
        ('change_of_plans', 'Change of Plans'),
        ('found_better_deal', 'Found a Better Deal'),
        ('no_longer_need', 'No Longer Need a Car'),
        ('error_in_booking', 'Error in Booking'),
        ('other', 'Other'),
    ]
    
    cancel_reason = forms.ChoiceField(choices=REASONS, required=False)
    comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

# 创建驾驶员表单集，默认只需要一个驾驶员信息
DriverFormSet = formset_factory(DriverForm, extra=0, can_delete=False, min_num=1, max_num=1, validate_min=True, validate_max=True)
