from django.db import models

class State(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_airport = models.BooleanField(default=False)
    opening_hours = models.CharField(max_length=255, default='Monday-Friday: 8AM-6PM, Saturday: 9AM-5PM, Sunday: Closed')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name}, {self.city}"
    
    class Meta:
        ordering = ['state', 'city', 'name']

class CityHighlight(models.Model):
    city = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    description = models.TextField()
    image_url = models.URLField()
    
    def __str__(self):
        return f"{self.city}, {self.state.code}"
