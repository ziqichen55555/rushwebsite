from django import forms
from .models import Booking, AddonOption

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
        
        if pickup_date and return_date and pickup_date >= return_date:
            raise forms.ValidationError('Return date must be after pickup date.')
        
        return cleaned_data

class AddonSelectionForm(forms.Form):
    """
    Form for selecting booking add-ons
    """
    def __init__(self, *args, **kwargs):
        addons = kwargs.pop('addons', [])
        super().__init__(*args, **kwargs)
        
        for addon in addons:
            max_qty = addon.max_quantity if addon.max_quantity > 0 else 10
            choices = [(0, 'None')] + [(i, str(i)) for i in range(1, max_qty + 1)]
            self.fields[f'addon_{addon.id}'] = forms.ChoiceField(
                choices=choices,
                initial=0,
                required=False,
                label='',
            )
    
    def get_selected_addons(self):
        """Returns a dictionary of addon IDs and their selected quantities"""
        selected_addons = {}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('addon_') and int(value) > 0:
                addon_id = int(field_name.split('_')[1])
                selected_addons[addon_id] = int(value)
        return selected_addons

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
