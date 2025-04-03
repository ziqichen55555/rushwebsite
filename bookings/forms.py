from django import forms
from .models import Booking
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
