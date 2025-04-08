from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from cars.models import Car
from locations.models import Location

class BookingOption(models.Model):
    """
    Additional options for car rentals
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    flat_fee = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    icon_class = models.CharField(max_length=50, default="fas fa-car")
    is_quantity_option = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='pickup_bookings')
    dropoff_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='dropoff_bookings')
    pickup_date = models.DateField()
    return_date = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    driver_age = models.PositiveIntegerField()
    
    # Extra options for the booking
    damage_waiver = models.BooleanField(default=False)
    extended_area = models.BooleanField(default=False)
    satellite_navigation = models.BooleanField(default=False)
    child_seats = models.PositiveIntegerField(default=0)
    additional_drivers = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s booking of {self.car} from {self.pickup_date} to {self.return_date}"
    
    @property
    def duration_days(self):
        delta = self.return_date - self.pickup_date
        return delta.days
        
    @property
    def options_cost(self):
        """Calculate the cost of added options"""
        cost = 0
        days = self.duration_days
        
        # Add costs for each option
        if self.damage_waiver:
            cost += 14 * days  # $14 per day
        
        if self.extended_area:
            cost += 150  # $150 flat fee
            
        if self.satellite_navigation:
            cost += 5 * days  # $5 per day
            
        if self.child_seats > 0:
            cost += 8 * days * self.child_seats  # $8 per day per seat
            
        if self.additional_drivers > 0:
            cost += 5 * days * self.additional_drivers  # $5 per day per driver
            
        return cost


class Driver(models.Model):
    """驾驶员信息模型"""
    
    OCCUPATION_CHOICES = [
        ('', '-- Please select --'),
        ('student', 'Student'),
        ('employed', 'Employed'),
        ('self_employed', 'Self-employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('other', 'Other'),
    ]
    
    # 个人信息
    last_name = models.CharField(_("Last Name"), max_length=100)
    first_name = models.CharField(_("First Name"), max_length=100)
    email = models.EmailField(_("Email"))
    date_of_birth = models.DateField(_("Date of Birth"))
    
    # 驾照信息
    license_number = models.CharField(_("License Number"), max_length=50)
    license_issued_in = models.CharField(_("Issued In"), max_length=100)
    license_expiry_date = models.DateField(_("Expiry Date"))
    license_is_lifetime = models.BooleanField(_("Life Time"), default=False)
    
    # 地址信息
    local_address = models.CharField(_("Local Address"), max_length=255, blank=True)
    address = models.CharField(_("Address"), max_length=255)
    city = models.CharField(_("City"), max_length=100)
    state = models.CharField(_("State"), max_length=100)
    postcode = models.CharField(_("Postcode"), max_length=20)
    country_of_residence = models.CharField(_("Country of Residence"), max_length=100, default="Australia")
    
    # 联系信息
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    mobile = models.CharField(_("Mobile"), max_length=20)
    fax = models.CharField(_("Fax"), max_length=20, blank=True)
    
    # 其他信息
    occupation = models.CharField(_("Occupation"), max_length=50, choices=OCCUPATION_CHOICES, blank=True)
    mailing_list = models.BooleanField(_("Subscribe to Mailing List"), default=False)
    
    # 关联信息
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='drivers', null=True)
    is_primary = models.BooleanField(_("Primary Driver"), default=False)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        """返回驾驶员全名"""
        return f"{self.first_name} {self.last_name}"
