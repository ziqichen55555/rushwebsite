from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from bookings.forms import BookingForm, DriverForm, CancellationForm
from locations.models import Location


class BookingFormTest(TestCase):
    """
    测试预订表单
    """
    
    def setUp(self):
        """
        设置测试数据
        """
        # 创建测试地点
        self.pickup_location = Location.objects.create(
            name='Sydney Airport',
            address='Sydney International Airport',
            city='Sydney',
            state='NSW',
            country='Australia'
        )
        
        self.dropoff_location = Location.objects.create(
            name='Melbourne CBD',
            address='Melbourne Central',
            city='Melbourne',
            state='VIC',
            country='Australia'
        )
        
        # 设置测试日期
        self.today = date.today()
        self.tomorrow = self.today + timedelta(days=1)
        self.next_week = self.today + timedelta(days=7)
    
    def test_valid_booking_form(self):
        """
        测试有效的预订表单
        """
        form_data = {
            'pickup_location': self.pickup_location.id,
            'dropoff_location': self.dropoff_location.id,
            'pickup_date': self.tomorrow,
            'return_date': self.next_week,
            'driver_age': 30
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_booking_form_past_pickup_date(self):
        """
        测试过去的取车日期
        """
        yesterday = self.today - timedelta(days=1)
        form_data = {
            'pickup_location': self.pickup_location.id,
            'dropoff_location': self.dropoff_location.id,
            'pickup_date': yesterday,  # 过去的日期
            'return_date': self.next_week,
            'driver_age': 30
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pickup_date', form.errors)
    
    def test_invalid_booking_form_return_before_pickup(self):
        """
        测试还车日期早于取车日期
        """
        form_data = {
            'pickup_location': self.pickup_location.id,
            'dropoff_location': self.dropoff_location.id,
            'pickup_date': self.next_week,
            'return_date': self.tomorrow,  # 早于取车日期
            'driver_age': 30
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        # 检查是否有相关错误信息
        self.assertTrue(any('return date' in str(error).lower() for error in form.errors.values()))
    
    def test_invalid_booking_form_underage_driver(self):
        """
        测试年龄过小的驾驶员
        """
        form_data = {
            'pickup_location': self.pickup_location.id,
            'dropoff_location': self.dropoff_location.id,
            'pickup_date': self.tomorrow,
            'return_date': self.next_week,
            'driver_age': 17  # 未满18岁
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('driver_age', form.errors)


class DriverFormTest(TestCase):
    """
    测试驾驶员表单
    """
    
    def test_valid_driver_form(self):
        """
        测试有效的驾驶员表单
        """
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': date(1990, 1, 15),
            'license_number': 'DL12345678',
            'license_issued_in': 'NSW',
            'license_expiry_date': date.today() + timedelta(days=365),
            'address': '123 Test Street',
            'city': 'Sydney',
            'state': 'NSW',
            'postcode': '2000',
            'country_of_residence': 'Australia',
            'mobile': '0400123456',
            'is_primary': True
        }
        form = DriverForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_driver_form_future_birth_date(self):
        """
        测试未来的出生日期
        """
        future_date = date.today() + timedelta(days=10)
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': future_date,  # 未来日期
            'license_number': 'DL12345678',
            'license_issued_in': 'NSW',
            'license_expiry_date': date.today() + timedelta(days=365),
            'address': '123 Test Street',
            'city': 'Sydney',
            'state': 'NSW',
            'postcode': '2000',
            'country_of_residence': 'Australia',
            'mobile': '0400123456',
            'is_primary': True
        }
        form = DriverForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)
    
    def test_invalid_driver_form_expired_license(self):
        """
        测试过期的驾照
        """
        past_date = date.today() - timedelta(days=10)
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': date(1990, 1, 15),
            'license_number': 'DL12345678',
            'license_issued_in': 'NSW',
            'license_expiry_date': past_date,  # 过期日期
            'address': '123 Test Street',
            'city': 'Sydney',
            'state': 'NSW',
            'postcode': '2000',
            'country_of_residence': 'Australia',
            'mobile': '0400123456',
            'is_primary': True
        }
        form = DriverForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('license_expiry_date', form.errors)
    
    def test_driver_form_lifetime_license(self):
        """
        测试终身驾照（无过期日期）
        """
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': date(1990, 1, 15),
            'license_number': 'DL12345678',
            'license_issued_in': 'NSW',
            'license_is_lifetime': True,  # 终身驾照
            'address': '123 Test Street',
            'city': 'Sydney',
            'state': 'NSW',
            'postcode': '2000',
            'country_of_residence': 'Australia',
            'mobile': '0400123456',
            'is_primary': True
        }
        form = DriverForm(data=form_data)
        self.assertTrue(form.is_valid())


class CancellationFormTest(TestCase):
    """
    测试取消预订表单
    """
    
    def test_valid_cancellation_form_with_reason(self):
        """
        测试有效的取消预订表单（带原因）
        """
        form_data = {
            'cancel_reason': 'change_of_plans',
            'comments': 'My plans have changed.'
        }
        form = CancellationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_cancellation_form_without_reason(self):
        """
        测试有效的取消预订表单（无原因）
        """
        form_data = {
            'cancel_reason': '',
            'comments': ''
        }
        form = CancellationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_cancellation_form_with_other_reason(self):
        """
        测试有效的取消预订表单（其他原因）
        """
        form_data = {
            'cancel_reason': 'other',
            'comments': 'I found a cheaper alternative.'
        }
        form = CancellationForm(data=form_data)
        self.assertTrue(form.is_valid())