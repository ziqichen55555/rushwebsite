from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from bookings.models import Booking, Driver
from cars.models import Car
from locations.models import Location


class BookingModelTest(TestCase):
    """
    测试 Booking 模型的基本功能
    """

    def setUp(self):
        """
        设置测试数据
        """
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建测试地点
        self.pickup_location = Location.objects.create(
            name='Sydney Airport',
            address='Sydney International Airport',
            city='Sydney',
            state='NSW',
            country='Australia',
            latitude=-33.9399,
            longitude=151.1753
        )
        
        self.dropoff_location = Location.objects.create(
            name='Melbourne CBD',
            address='Melbourne Central',
            city='Melbourne',
            state='VIC',
            country='Australia',
            latitude=-37.8136,
            longitude=144.9631
        )
        
        # 创建测试车辆
        self.car = Car.objects.create(
            make='Toyota',
            model='Camry',
            year=2023,
            category='comfort',
            daily_rate=70.00,
            transmission='automatic',
            fuel_type='gasoline',
            seats=5,
            is_available=True
        )
        
        # 创建测试预订
        self.today = date.today()
        self.booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            pickup_location=self.pickup_location,
            dropoff_location=self.dropoff_location,
            pickup_date=self.today,
            return_date=self.today + timedelta(days=3),
            driver_age=30,
            status='pending',
            total_cost=210.00
        )

    def test_booking_creation(self):
        """
        测试预订创建和基本属性
        """
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.car, self.car)
        self.assertEqual(self.booking.pickup_location, self.pickup_location)
        self.assertEqual(self.booking.dropoff_location, self.dropoff_location)
        self.assertEqual(self.booking.pickup_date, self.today)
        self.assertEqual(self.booking.return_date, self.today + timedelta(days=3))
        self.assertEqual(self.booking.status, 'pending')
        self.assertEqual(self.booking.total_cost, 210.00)

    def test_booking_string_representation(self):
        """
        测试预订的字符串表示
        """
        expected_string = f"{self.user.username} - {self.car} ({self.pickup_date} to {self.return_date})"
        self.assertEqual(str(self.booking), expected_string)

    def test_booking_duration_days(self):
        """
        测试预订天数计算
        """
        self.assertEqual(self.booking.duration_days(), 3)
        
        # 测试同一天的预订
        same_day_booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            pickup_location=self.pickup_location,
            dropoff_location=self.dropoff_location,
            pickup_date=self.today,
            return_date=self.today,
            driver_age=30,
            status='pending',
            total_cost=70.00
        )
        self.assertEqual(same_day_booking.duration_days(), 1)


class DriverModelTest(TestCase):
    """
    测试 Driver 模型的基本功能
    """

    def setUp(self):
        """
        设置测试数据
        """
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建测试地点
        self.pickup_location = Location.objects.create(
            name='Sydney Airport',
            city='Sydney',
            state='NSW',
            country='Australia'
        )
        
        self.dropoff_location = Location.objects.create(
            name='Melbourne CBD',
            city='Melbourne',
            state='VIC',
            country='Australia'
        )
        
        # 创建测试车辆
        self.car = Car.objects.create(
            make='Toyota',
            model='Camry',
            year=2023,
            category='comfort',
            daily_rate=70.00,
            is_available=True
        )
        
        # 创建测试预订
        self.today = date.today()
        self.booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            pickup_location=self.pickup_location,
            dropoff_location=self.dropoff_location,
            pickup_date=self.today,
            return_date=self.today + timedelta(days=3),
            driver_age=30,
            status='pending',
            total_cost=210.00
        )
        
        # 创建测试驾驶员
        self.driver = Driver.objects.create(
            booking=self.booking,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            date_of_birth=date(1990, 1, 15),
            license_number='DL12345678',
            license_issued_in='NSW',
            license_expiry_date=date.today() + timedelta(days=365),
            address='123 Test Street',
            city='Sydney',
            state='NSW',
            postcode='2000',
            country_of_residence='Australia',
            mobile='0400123456',
            is_primary=True
        )

    def test_driver_creation(self):
        """
        测试驾驶员创建和基本属性
        """
        self.assertEqual(self.driver.booking, self.booking)
        self.assertEqual(self.driver.first_name, 'John')
        self.assertEqual(self.driver.last_name, 'Doe')
        self.assertEqual(self.driver.email, 'john.doe@example.com')
        self.assertEqual(self.driver.license_number, 'DL12345678')
        self.assertTrue(self.driver.is_primary)

    def test_get_full_name(self):
        """
        测试驾驶员全名方法
        """
        self.assertEqual(self.driver.get_full_name(), 'John Doe')
        
        # 测试只有名字的情况
        self.driver.last_name = ''
        self.driver.save()
        self.assertEqual(self.driver.get_full_name(), 'John')
        
        # 测试只有姓氏的情况
        self.driver.first_name = ''
        self.driver.last_name = 'Doe'
        self.driver.save()
        self.assertEqual(self.driver.get_full_name(), 'Doe')