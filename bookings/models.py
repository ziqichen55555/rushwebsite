from django.db import models
from django.contrib.auth.models import User
from cars.models import Car
from locations.models import Location

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
    
    def __str__(self):
        return f"{self.user.username}'s booking of {self.car} from {self.pickup_date} to {self.return_date}"
    
    @property
    def duration_days(self):
        delta = self.return_date - self.pickup_date
        return delta.days
