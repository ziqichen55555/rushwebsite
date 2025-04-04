from django.db import models
from django.contrib.auth.models import User
from cars.models import Car
from locations.models import Location
from decimal import Decimal

class AddonOption(models.Model):
    """
    Additional rental options that users can add to their booking
    """
    PRICING_TYPE_CHOICES = [
        ('per_day', 'Per Day'),
        ('flat_fee', 'Flat Fee'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, help_text="Font Awesome icon class (e.g., 'fa-shield-alt')")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    pricing_type = models.CharField(max_length=10, choices=PRICING_TYPE_CHOICES, default='per_day')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    max_quantity = models.PositiveIntegerField(default=1, help_text="Maximum quantity that can be selected (0 for unlimited)")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']

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
    addons = models.ManyToManyField(AddonOption, through='BookingAddon', blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s booking of {self.car} from {self.pickup_date} to {self.return_date}"
    
    @property
    def duration_days(self):
        delta = self.return_date - self.pickup_date
        return delta.days
    
    @property
    def base_cost(self):
        """Returns the cost of just the car rental without addons"""
        return self.car.daily_rate * self.duration_days
    
    @property
    def addons_cost(self):
        """Returns the total cost of all addons"""
        addon_total = Decimal('0.00')
        for booking_addon in self.bookingaddon_set.all():
            if booking_addon.addon.pricing_type == 'per_day':
                addon_total += booking_addon.addon.price * self.duration_days * booking_addon.quantity
            else:  # flat_fee
                addon_total += booking_addon.addon.price * booking_addon.quantity
        return addon_total

class BookingAddon(models.Model):
    """
    Junction table for Booking-AddonOption with additional field for quantity
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    addon = models.ForeignKey(AddonOption, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.addon.name} for {self.booking}"
    
    class Meta:
        unique_together = ('booking', 'addon')
