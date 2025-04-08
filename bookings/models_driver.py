"""
驾驶员模型定义
包含与预订相关的驾驶员信息模型
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

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
    
    # 基本信息
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
    
    # 关联字段
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='drivers', null=True)
    is_primary = models.BooleanField(_("Primary Driver"), default=False)
    
    # 创建和更新时间
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