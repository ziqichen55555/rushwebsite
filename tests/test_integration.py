from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
import re
from bookings.models import Booking, Driver
from cars.models import Car
from locations.models import Location
from accounts.models import Profile


class BookingFlowTest(TestCase):
    """
    测试完整的预订流程
    """
    
    def setUp(self):
        """
        设置测试数据
        """
        self.client = Client()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 确保用户有关联的个人资料
        self.profile = Profile.objects.get_or_create(user=self.user)[0]
        
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
        
        # 登录用户
        self.client.login(username='testuser', password='testpassword')
        
        # 设置测试日期
        self.today = date.today()
        self.tomorrow = self.today + timedelta(days=1)
        self.next_week = self.today + timedelta(days=7)
    
    def test_complete_booking_flow(self):
        """
        测试完整的预订流程，从创建到支付成功
        """
        # 步骤1：创建预订
        create_booking_response = self.client.post(reverse('create_booking', args=[self.car.id]), {
            'pickup_location': self.pickup_location.id,
            'dropoff_location': self.dropoff_location.id,
            'pickup_date': self.tomorrow.strftime('%Y-%m-%d'),
            'return_date': self.next_week.strftime('%Y-%m-%d'),
            'driver_age': 30
        })
        
        # 检查是否重定向到驾驶员信息页面
        self.assertEqual(create_booking_response.status_code, 302)
        self.assertTrue('/drivers/' in create_booking_response.url)
        
        # 从重定向URL中提取临时预订ID
        temp_booking_id = create_booking_response.url.split('/')[-2]
        
        # 步骤2：添加驾驶员信息
        driver_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1',
            'form-0-first_name': 'John',
            'form-0-last_name': 'Doe',
            'form-0-email': 'john.doe@example.com',
            'form-0-date_of_birth': '1990-01-15',
            'form-0-license_number': 'DL12345678',
            'form-0-license_issued_in': 'NSW',
            'form-0-license_expiry_date': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'form-0-address': '123 Test Street',
            'form-0-city': 'Sydney',
            'form-0-state': 'NSW',
            'form-0-postcode': '2000',
            'form-0-country_of_residence': 'Australia',
            'form-0-mobile': '0400123456',
            'form-0-is_primary': 'on'
        }
        
        add_drivers_response = self.client.post(
            reverse('add_drivers', args=[temp_booking_id]),
            driver_data
        )
        
        # 检查是否重定向到添加选项页面
        self.assertEqual(add_drivers_response.status_code, 302)
        self.assertTrue('/options/' in add_drivers_response.url)
        
        # 步骤3：添加选项
        options_response = self.client.post(
            reverse('add_options', args=[temp_booking_id]),
            {
                'damage_waiver': 'on',
                'satellite_navigation': 'on',
                'child_seats': 1
            }
        )
        
        # 检查是否重定向到确认页面
        self.assertEqual(options_response.status_code, 302)
        self.assertTrue('/confirm/' in options_response.url)
        
        # 步骤4：确认预订
        confirm_response = self.client.post(
            reverse('confirm_booking', args=[temp_booking_id]),
            {'confirm': 'true'}
        )
        
        # 检查是否重定向到支付页面
        self.assertEqual(confirm_response.status_code, 302)
        self.assertTrue('/payment/' in confirm_response.url)
        
        # 步骤5：处理支付（模拟）
        process_payment_response = self.client.post(
            reverse('process_payment', args=[temp_booking_id]),
            {'payment_method': 'card'}
        )
        
        # 检查是否重定向到支付成功页面
        self.assertEqual(process_payment_response.status_code, 302)
        booking_id_match = re.search(r'/bookings/payment-success/(\d+)/', process_payment_response.url)
        self.assertIsNotNone(booking_id_match)
        booking_id = int(booking_id_match.group(1))
        
        # 步骤6：验证预订是否成功创建
        booking = Booking.objects.get(id=booking_id)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.car, self.car)
        self.assertEqual(booking.pickup_location, self.pickup_location)
        self.assertEqual(booking.dropoff_location, self.dropoff_location)
        self.assertEqual(booking.status, 'confirmed')
        
        # 验证驾驶员是否正确创建
        driver = Driver.objects.filter(booking=booking).first()
        self.assertIsNotNone(driver)
        self.assertEqual(driver.first_name, 'John')
        self.assertEqual(driver.last_name, 'Doe')
        self.assertTrue(driver.is_primary)
        
        # 验证预订选项是否正确保存
        self.assertTrue(booking.damage_waiver)
        self.assertTrue(booking.satellite_navigation)
        self.assertEqual(booking.child_seats, 1)
        
        # 步骤7：验证用户可以查看预订详情
        booking_detail_response = self.client.get(reverse('booking_detail', args=[booking.id]))
        self.assertEqual(booking_detail_response.status_code, 200)
        self.assertTemplateUsed(booking_detail_response, 'bookings/booking_detail.html')


class UserRegistrationAndProfileTest(TestCase):
    """
    测试用户注册和个人资料管理
    """
    
    def setUp(self):
        """
        设置测试数据
        """
        self.client = Client()
    
    def test_user_registration_and_profile_management(self):
        """
        测试用户注册和个人资料管理
        """
        # 步骤1：注册新用户
        register_response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        })
        
        # 检查是否重定向到登录页面
        self.assertEqual(register_response.status_code, 302)
        self.assertRedirects(register_response, reverse('login'))
        
        # 验证用户是否成功创建
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        
        # 验证个人资料是否自动创建
        self.assertTrue(hasattr(user, 'profile'))
        
        # 步骤2：登录
        login_response = self.client.post(reverse('login'), {
            'username': 'newuser',
            'password': 'securepassword123',
        })
        
        # 检查是否重定向到首页
        self.assertEqual(login_response.status_code, 302)
        
        # 步骤3：访问个人资料页面
        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertTemplateUsed(profile_response, 'accounts/profile.html')
        
        # 步骤4：更新个人资料
        update_profile_response = self.client.post(reverse('profile'), {
            'username': 'newuser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone': '0412345678',
            'address': '123 Main St, Sydney',
            'date_of_birth': '1990-05-15',
            'license_number': 'DL98765432',
        })
        
        # 检查是否重定向回个人资料页面
        self.assertEqual(update_profile_response.status_code, 302)
        self.assertRedirects(update_profile_response, reverse('profile'))
        
        # 刷新用户和个人资料
        user.refresh_from_db()
        profile = user.profile
        
        # 验证更新是否成功
        self.assertEqual(user.email, 'updated@example.com')
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(profile.phone, '0412345678')
        self.assertEqual(profile.license_number, 'DL98765432')
        
        # 步骤5：添加驾驶员信息
        add_driver_response = self.client.post(reverse('add_driver'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'date_of_birth': '1990-01-15',
            'license_number': 'DL12345678',
            'license_issued_in': 'NSW',
            'license_expiry_date': (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'address': '123 Test Street',
            'city': 'Sydney',
            'state': 'NSW',
            'postcode': '2000',
            'country_of_residence': 'Australia',
            'mobile': '0400123456',
            'is_primary': 'on',
        })
        
        # 检查是否重定向回个人资料页面
        self.assertEqual(add_driver_response.status_code, 302)
        self.assertRedirects(add_driver_response, reverse('profile'))
        
        # 刷新个人资料
        profile.refresh_from_db()
        
        # 验证驾驶员是否成功添加
        self.assertEqual(profile.drivers.count(), 1)
        driver = profile.drivers.first()
        self.assertEqual(driver.first_name, 'John')
        self.assertEqual(driver.last_name, 'Doe')
        self.assertTrue(driver.is_primary)
        
        # 步骤6：访问我的预订页面
        bookings_response = self.client.get(reverse('user_bookings'))
        self.assertEqual(bookings_response.status_code, 200)
        self.assertTemplateUsed(bookings_response, 'accounts/user_bookings.html')