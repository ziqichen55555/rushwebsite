from django.db import models
from django.contrib.auth.models import User
from bookings.models import Driver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=30, blank=True)
    drivers = models.ManyToManyField(Driver, related_name='profiles', blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def get_primary_driver(self):
        """获取用户的主驾驶员信息"""
        drivers = self.drivers.filter(is_primary=True).first()
        if not drivers:
            drivers = self.drivers.first()
        return drivers
