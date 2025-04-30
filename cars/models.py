from django.db import models
from locations.models import Location
from django.utils import timezone

class AuditModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class VehicleImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vehicle_images/')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class VehicleType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class VehicleCategoryType(AuditModelMixin):
    category_type = models.CharField(max_length=50)
    rate_type = models.CharField(max_length=50)
    web_available = models.BooleanField(default=False)
    ordering = models.IntegerField(default=0)
    
    def __str__(self):
        return self.category_type
    
    class Meta:
        ordering = ['ordering', 'category_type']

class VehicleCategory(AuditModelMixin):
    REGION_CHOICES = [
        ('melbourne', 'Melbourne'),
        ('sydney', 'Sydney'),
        ('brisbane', 'Brisbane'),
        ('perth', 'Perth'),
        ('adelaide', 'Adelaide'),
        ('gold_coast', 'Gold Coast'),
        ('xi_an', 'Xi An'),
        ('beijing', 'Beijing'),
        ('shanghai', 'Shanghai'),
        ('guangzhou', 'Guangzhou'),
        ('shenzhen', 'Shenzhen'),
        ('hangzhou', 'Hangzhou'),
        ('nanjing', 'Nanjing'),
    ]
    
    name = models.CharField(max_length=100, blank=True, null=True)
    category_type = models.ForeignKey(VehicleCategoryType, on_delete=models.CASCADE, related_name='categories')
    vehicle_category = models.CharField(max_length=100)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)  
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default='melbourne')
    renting_category = models.BooleanField(default=False)
    sipp_code = models.CharField(max_length=10, blank=True, null=True)
    age_youngest_driver = models.IntegerField(default=21)
    num_adults = models.IntegerField(default=0)
    num_children = models.IntegerField(default=0)
    num_large_case = models.IntegerField(default=0)
    num_small_case = models.IntegerField(default=0)
    emission_rate = models.CharField(max_length=50, blank=True, null=True)
    vehicle_desc_url = models.URLField(blank=True, null=True)
    image_upload = models.ForeignKey(VehicleImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='categories')
    friendly_description = models.TextField(blank=True, null=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    locations = models.ManyToManyField(Location, related_name='available_vehicles')
    
    # Comparison pricing fields
    comparison_provider1_name = models.CharField(max_length=50, blank=True)
    comparison_provider1_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    comparison_provider2_name = models.CharField(max_length=50, blank=True)
    comparison_provider2_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        display_name = self.name if self.name else self.vehicle_category
        return f"{display_name} ({self.get_region_display()})"
    
    def get_image_url(self):
        if self.image_upload and self.image_upload.image:
            return self.image_upload.image.url
        return '/static/images/car-placeholder.jpg'
    
    class Meta:
        verbose_name_plural = 'Vehicle Categories'
        ordering = ['category_type__ordering', 'vehicle_category']

class VehicleFeature(models.Model):
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE, related_name='features')
    feature = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, default="fas fa-check")
    
    def __str__(self):
        return self.feature

# 保留旧模型以兼容现有代码，但将它们链接到新模型
class CarCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    vehicle_category_type = models.ForeignKey(VehicleCategoryType, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Car Categories (Legacy)'

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
    vehicle_category = models.ForeignKey(VehicleCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='legacy_cars')
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
