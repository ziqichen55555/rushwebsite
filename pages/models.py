from django.db import models

from cars.models import VehicleCategory, VehicleFuel, VehicleMake, VehicleModel, VehicleCategory,  AuditModelMixin




class Testimonial(models.Model):
    """用户评价模型"""
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, choices=[(i, str(i)) for i in range(1, 6)])
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating}星"




class Country(AuditModelMixin):
    name = models.CharField(max_length=100, default='Australia')
    sales_tax_name = models.CharField(max_length=100, blank=True, null=True)
    sales_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sales_tax_start_date = models.DateField(blank=True, null=True)
    document_culture = models.CharField(max_length=10, default='en-AU')
    system_culture = models.CharField(max_length=10, default='en-AU')
    currency = models.CharField(max_length=10, default='AUD')
    currency_symbol = models.CharField(max_length=10, default='$')
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Countries"
        managed = False
        db_table = 'app_country'

class StateProvince(AuditModelMixin):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    state_tax_name = models.CharField(max_length=100, blank=True, null=True)
    state_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    state_tax_start_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['country', 'name']
        verbose_name_plural = "States/Provinces"
        managed = False
        db_table = 'app_stateprovince'
class City(AuditModelMixin):
    state = models.ForeignKey(StateProvince, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['state', 'name']
        verbose_name_plural = "Cities"
        managed = False
        db_table = 'app_city'

class VehicleFuel(AuditModelMixin):
    YES_NO_CHOICES = (
        (True, 'Yes'),
        (False, 'No'),
    )
    fuel_type = models.CharField(max_length=100)
    is_electric = models.BooleanField(default=False, choices=YES_NO_CHOICES)
    fuel_unit = models.CharField(max_length=50, default='Liter')
    fuel_unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_default = models.BooleanField(default=False, choices=YES_NO_CHOICES)
    fuel_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['fuel_type']
        managed = False
        db_table = 'app_vehiclefuel'
class VehicleMake(AuditModelMixin):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        managed = False
        db_table = 'app_vehiclemake'
    
class VehicleModel(AuditModelMixin):
    make = models.ForeignKey(VehicleMake, on_delete=models.DO_NOTHING, related_name='models')
    model_name = models.CharField(max_length=100)
    fuel_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)

    class Meta:
        ordering = ['model_name']
        managed = False 
        db_table = 'app_vehiclemodel'



class CarSubscription(models.Model):
    class Meta:
        app_label = 'rushwebsite'
        verbose_name = ('Car Subscription')
        verbose_name_plural = ('Car Subscriptions')
        ordering = ['-created_at']
        db_table = 'rushwebsite_carsubscription'
        managed = False
    STATUS_CHOICES = (
        ('available', ('Available')),
        ('unavailable', ('Unavailable')),
    )

    vehicle_category = models.ForeignKey(
        VehicleCategory,
        on_delete=models.DO_NOTHING,
        verbose_name=('Vehicle Category')
    )
    location = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        verbose_name=('Location')
    )
    fuel_type = models.ForeignKey(
        VehicleFuel,
        on_delete=models.DO_NOTHING,
        verbose_name=('Fuel Type')
    )
    model = models.ForeignKey(
        VehicleModel,
        on_delete=models.DO_NOTHING,
        verbose_name=('Vehicle Model')
    )
    
    # Additional fields
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=('Registration Number')
    )
    year = models.IntegerField(verbose_name=('Year'))
    mileage = models.IntegerField(verbose_name=('Mileage'))
    subscription_plan1 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=('subscription plan1(3months)')
    )
    subscription_plan2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=('subscription plan2(6months)')
    )
    subscription_plan3 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=('subscription plan3(9months)')
    )
    
    # Multiple image fields to match your form
    image1 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=('Car Image 1'),
        blank=True,
        null=True,
        help_text=('Upload car image (maximum 300kb)')
    )
    image2 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=('Car Image 2'),
        blank=True,
        null=True,
        help_text=('Upload car image (maximum 300kb)')
    )
    image3 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=('Car Image 3'),
        blank=True,
        null=True,
        help_text=('Upload car image (maximum 300kb)')
    )
    image4 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=('Car Image 4'),
        blank=True,
        null=True,
        help_text=('Upload car image (maximum 300kb)')
    )
    image5 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=('Car Image 5'),
        blank=True,
        null=True,
        help_text=('Upload car image (maximum 300kb)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name=('Status')
    )
    description = models.TextField(
        blank=True,
        verbose_name=('Description')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=('Updated At')
    )

    def __str__(self):
        return f"{self.model} - {self.registration_number}"
    
    def get_images(self):
        """Return list of all non-empty images"""
        images = []
        for i in range(1, 6):
            image = getattr(self, f'image{i}')
            if image:
                images.append(image)
        return images
    
    def get_primary_image(self):
        """Return the first available image"""
        for i in range(1, 6):
            image = getattr(self, f'image{i}')
            if image:
                return image
        return None