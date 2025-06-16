from django.db import models
from locations.models import Location
from django.utils import timezone


class AuditModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        managed = False 

class VehicleImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='vehicle_images/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'app_vehicleimage'
        managed = False

class VehicleType(AuditModelMixin):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'app_vehicletype'
        managed = False


class VehicleCategoryType(AuditModelMixin):
    category_type = models.CharField(max_length=50)
    rate_type = models.CharField(max_length=50)
    web_available = models.BooleanField(default=False)
    ordering = models.IntegerField(default=0)

    def __str__(self):
        return self.category_type

    class Meta:
        db_table = 'app_vehiclecategorytype'
        ordering = ['ordering', 'category_type']
        managed = False


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

    
    name = models.CharField(max_length=100,blank=True, null=True)
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

    class Meta:
        ordering = ['category_type', 'vehicle_category']
        verbose_name_plural = "Vehicle Categories"
        managed = False

    def __str__(self):
        return f"{self.category_type.category_type} - {self.vehicle_category}"


    # Compatibility methods to match Car model interface
    @property
    def make(self):
        """Return a make value for compatibility with Car model"""
        parts = self.vehicle_category.split()
        return parts[0] if parts else ""

    @property
    def model(self):
        """Return a model value for compatibility with Car model"""
        parts = self.vehicle_category.split()
        return " ".join(parts[1:]) if len(parts) > 1 else self.vehicle_category

    @property
    def seats(self):
        """Return seats for compatibility with Car model"""
        return self.num_adults + self.num_children

    @property
    def bags(self):
        """Return bags for compatibility with Car model"""
        return self.num_large_case + self.num_small_case

    class Meta:
        db_table = 'app_vehiclecategory'
        verbose_name_plural = 'Vehicle Categories'
        ordering = ['category_type__ordering', 'vehicle_category']


class VehicleFeature(models.Model):
    vehicle_category = models.ForeignKey(VehicleCategory,
                                         on_delete=models.CASCADE,
                                         related_name='features')
    feature = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, default="fas fa-check")

    def __str__(self):
        return self.feature

    class Meta:
        db_table = 'cars_vehiclefeature'



# 保留旧模型以兼容现有代码，但将它们链接到新模型
class CarCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    vehicle_category_type = models.ForeignKey(VehicleCategoryType,
                                              on_delete=models.SET_NULL,
                                              null=True,
                                              blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'cars_carcategory'
        verbose_name_plural = 'Car Categories (Legacy)'


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
    def __str__(self):
        return self.fuel_type


class VehicleMake(AuditModelMixin):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        managed = False
        db_table = 'app_vehiclemake'
    def __str__(self):
        return self.name

class VehicleModel(AuditModelMixin):
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE, related_name='models')
    model_name = models.CharField(max_length=100)
    fuel_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)

    class Meta:
        ordering = ['model_name']
        managed = False
        db_table = 'app_vehiclemodel'   
    def __str__(self):
        return self.model_name
# System Settings Models
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
    def __str__(self):
        return self.name

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
        db_table = 'app_stateprovince'
        managed = False
    def __str__(self):
        return self.name

class City(AuditModelMixin):
    state = models.ForeignKey(StateProvince, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['state', 'name']
        verbose_name_plural = "Cities"
        db_table = 'app_city'
        managed = False
    def __str__(self):
        return self.name
    
class Airport(AuditModelMixin):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='airports')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)

    class Meta:
        ordering = ['city', 'name']
        db_table = 'app_airport'
        managed = False
    def __str__(self):
        return self.name

class MasterLocation(AuditModelMixin):
    master_location_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['master_location_name']
        db_table = 'app_masterlocation'
        managed = False
    def __str__(self):
        return self.master_location_name
    
class Location(AuditModelMixin):
    location_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, default='')
    renting_location = models.BooleanField(default=True)
    prefix = models.CharField(max_length=3, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='locations')
    state = models.ForeignKey(StateProvince, on_delete=models.CASCADE, related_name='locations')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='locations')
    master_location = models.ForeignKey(MasterLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='locations')
    airport = models.ForeignKey(Airport, on_delete=models.SET_NULL, null=True, blank=True, related_name='locations')
    postcode = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    free_phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gmt_difference = models.CharField(max_length=10, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    licence_no = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    currency_symbol = models.CharField(max_length=1, blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    payment_details = models.TextField(blank=True, null=True)
    map_url = models.URLField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        ordering = ['location_name']
        db_table = 'app_location'
        managed = False 
    def __str__(self):
        return self.location_name


class Car(AuditModelMixin):
    # 其他必要字段
    is_available = models.BooleanField(default=True, verbose_name=('Is Available'))
    available_for_booking = models.BooleanField(default=True, verbose_name=('Available for Booking'))
    is_virtual = models.BooleanField(default=False, verbose_name=('Is Virtual'))
    is_utilize = models.BooleanField(default=True, verbose_name=('Is Utilize'))
    
    # 车辆基本信息
    registration_no = models.CharField(max_length=20, blank=True, null=True, verbose_name=('Registration No'))
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, null=True, blank=True, related_name='cars', verbose_name=('Model'))
    category = models.ForeignKey(VehicleCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='cars', verbose_name=('Category'))
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars', verbose_name=('Vehicle Type'))
    year = models.PositiveIntegerField(blank=True, null=True, verbose_name=('Year'))
    # 位置信息
    owning_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_cars', verbose_name=('Owning Location'))
    currently_located = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_cars', verbose_name=('Currently Located'))
    fleet_no = models.CharField(max_length=20, blank=True, null=True, verbose_name=('Fleet No'))
    colour = models.CharField(max_length=50, blank=True, null=True, verbose_name=('Colour'))
    transmission = models.CharField(max_length=20, blank=True, null=True, verbose_name=('Transmission'))
    fuel_type = models.ForeignKey(VehicleFuel, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars', verbose_name=('Fuel Type'))
    fuel_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0, verbose_name=('Fuel Capacity'))
    current_kms = models.IntegerField(blank=True, null=True, default=0, verbose_name=('Current KMs'))

    date_off_fleet = models.DateField(blank=True, null=True, verbose_name= ('Date Off Fleet'))
    rego_expiration_date = models.DateField(blank=True, null=True, verbose_name=('Registration Expiration Date'))
    rwc_cof_date = models.DateField(blank=True, null=True, verbose_name=('RWC/COF Date'))
    electrical_date = models.DateField(blank=True, null=True, verbose_name=('Electrical Date'))
    
    # 其他信息
    grade = models.CharField(max_length=20, blank=True, null=True, verbose_name=('Grade'))
    radio_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=('Radio Code'))
    pm_schedule_category = models.CharField(max_length=100, blank=True, null=True, verbose_name=('PM Schedule Category'))
    pm_base_date = models.DateField(blank=True, null=True, verbose_name=('PM Base Date'))
    pm_base_mileage = models.IntegerField(blank=True, null=True, verbose_name=('PM Base Mileage'))
    road_user_expiry_kms = models.IntegerField(blank=True, null=True, verbose_name=('Road User Expiry KMs'))
    emission_rate = models.CharField(max_length=50, blank=True, null=True, verbose_name=('Emission Rate'))
    notes = models.TextField(blank=True, null=True, verbose_name=('Notes'))
    
    
        
    class Meta:
        ordering = ['id', 'registration_no']
        verbose_name = ('Car')
        verbose_name_plural = ('Cars')
        managed = False
        db_table = 'app_car'
    def __str__(self):
        if self.registration_no:
            return f"{self.registration_no} ({self.model})"
        return f"Car #{self.id}"
    
