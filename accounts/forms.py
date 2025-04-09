from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Profile
from bookings.models import Driver
from bookings.forms import DriverForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'date_of_birth', 'license_number']

class ProfileDriverForm(DriverForm):
    """
    在用户个人资料中添加驾驶员信息的表单，
    继承自DriverForm，但进行了适当调整
    """
    is_primary = forms.BooleanField(
        label=_("Set as Primary Driver"),
        required=False,
        initial=True,
        help_text=_("This driver will be automatically selected for new bookings")
    )
    
    class Meta(DriverForm.Meta):
        # 使用与DriverForm相同的字段，但移除booking相关字段
        fields = [
            'first_name', 'last_name', 'email', 'date_of_birth',
            'license_number', 'license_issued_in', 'license_expiry_date', 'license_is_lifetime',
            'address', 'local_address', 'city', 'state', 'postcode', 'country_of_residence',
            'phone', 'mobile', 'fax', 'occupation', 'mailing_list', 'is_primary'
        ]
