from django.db import models
from cars.models import Car, CarCategory, VehicleCategory, VehicleCategoryType,VehicleMake,VehicleModel,VehicleFuel,VehicleType,VehicleImage
from django.utils.translation import gettext_lazy as _




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



class CarSubscription(models.Model):
    class Meta:
        app_label = 'rushwebsite'
        verbose_name = _('Car Subscription')
        verbose_name_plural = _('Car Subscriptions')
        ordering = ['-created_at']

    STATUS_CHOICES = (
        ('available', _('Available')),
        ('unavailable', _('Unavailable')),
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        verbose_name=_('Car'),
        related_name='rushwebsite_carsubscriptions'
    )
    
    
    # Additional fields
    
    subscription_plan1 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('subscription plan1(3months)')
    )
    subscription_plan2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('subscription plan2(6months)')
    )
    subscription_plan3 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('subscription plan3(9months)')
    )
    seat_number = models.IntegerField(verbose_name=_('Seat Number'))
    # Multiple image fields to match your form
    image1 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=_('Car Image 1'),
        blank=True,
        null=True,
        help_text=_('Upload car image (maximum 300kb)')
    )
    image2 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=_('Car Image 2'),
        blank=True,
        null=True,
        help_text=_('Upload car image (maximum 300kb)')
    )
    image3 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=_('Car Image 3'),
        blank=True,
        null=True,
        help_text=_('Upload car image (maximum 300kb)')
    )
    image4 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=_('Car Image 4'),
        blank=True,
        null=True,
        help_text=_('Upload car image (maximum 300kb)')
    )
    image5 = models.ImageField(
        upload_to='car_subscription_images/',
        verbose_name=_('Car Image 5'),
        blank=True,
        null=True,
        help_text=_('Upload car image (maximum 300kb)')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name=_('Status')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    def __str__(self):
        return f"{self.car.id}"
    
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
    
class CarFeature(models.Model):
    car = models.ForeignKey(Car,
                            on_delete=models.CASCADE,
                            related_name='features')
    feature = models.CharField(max_length=100)

    def __str__(self):
        return self.feature

    class Meta:
        db_table = 'cars_carfeature'

class RushSubscriptionEnquiry(models.Model):
    # 所选订阅车辆（可为空）
    vehicle = models.ForeignKey(
        Car,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=("Selected Vehicle")
    )

    # 用户选择的订阅价格（例如每月价格）
    subscription_plan = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=("Subscription Price")
    )

    # 存储10个问题的答案（JSON）
    enquiry_answers = models.JSONField(
        null=True,
        blank=True,
        verbose_name=("Form Answers")
    )
    source_page = models.CharField(max_length=100, blank=True)
    # 联系人信息
    name = models.CharField(max_length=100, verbose_name=("Full Name"))
    email = models.EmailField(verbose_name=("Email Address"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=("Phone Number"))
    contact_method = models.CharField(
        max_length=10,
        choices=[('Email', 'Email'), ('Phone', 'Phone')],
        default='Email',
        verbose_name=("Preferred Contact Method")
    )


    # 提交时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=("Submitted At"))

    class Meta:
        verbose_name = ("Rush Subscription Enquiry")
        verbose_name_plural = ("Rush Subscription Enquiries")
        ordering = ['-created_at']
        db_table = 'rushwebsite_rushsubscriptionenquiry'
    def __str__(self):
        return f'{self.name} ({self.email}) - {self.created_at.strftime("%Y-%m-%d")}'
    @property  
    def inferred_type(self):
        if self.vehicle and self.subscription_plan:
            return 'subscription'
        elif self.source_page == 'contact-us':
            return 'contact'
        else:
            return 'general'