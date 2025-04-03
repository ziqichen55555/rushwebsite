from django.db import models
from locations.models import Location

class CarCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Car Categories'

class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('A', 'Automatic'),
        ('M', 'Manual'),
    ]
    
    name = models.CharField(max_length=100)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    category = models.ForeignKey(CarCategory, on_delete=models.CASCADE)
    seats = models.PositiveIntegerField()
    bags = models.PositiveIntegerField()
    doors = models.PositiveIntegerField()
    transmission = models.CharField(max_length=1, choices=TRANSMISSION_CHOICES)
    air_conditioning = models.BooleanField(default=True)
    image_url = models.URLField()
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    locations = models.ManyToManyField(Location, related_name='available_cars')
    
    # Comparison pricing fields
    comparison_provider1_name = models.CharField(max_length=50, blank=True)
    comparison_provider1_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    comparison_provider2_name = models.CharField(max_length=50, blank=True)
    comparison_provider2_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
    
    def get_display_name(self):
        return f"{self.make} {self.model}"

class CarFeature(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='features')
    feature = models.CharField(max_length=100)
    
    def __str__(self):
        return self.feature
