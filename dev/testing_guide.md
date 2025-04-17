# Rush Car Rental 测试指南

## 一、测试概述

Rush Car Rental 项目需要全面的测试策略，确保系统的稳定性、可靠性和安全性。本文档提供了测试的类型、范围和实施方法的详细说明。

### 测试层次

1. **单元测试**：测试独立的功能单元
2. **集成测试**：测试多个组件之间的交互
3. **功能测试**：测试完整的用户场景
4. **性能测试**：测试系统在不同负载下的性能
5. **安全测试**：验证系统的安全机制

### 测试工具

- Django 测试框架
- pytest
- Selenium (Web UI 测试)
- Coverage.py (代码覆盖率分析)
- locust (负载测试)

## 二、单元测试

### 模型测试

```python
# bookings/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta
from bookings.models import Booking, Driver
from cars.models import Car
from locations.models import Location

class BookingModelTest(TestCase):
    def setUp(self):
        """设置测试数据"""
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
            luggage_capacity=3,
            air_conditioning=True,
            is_available=True,
            image='cars/camry.jpg'
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
    
    def test_booking_creation(self):
        """测试预订对象创建"""
        self.assertEqual(self.booking.user.username, 'testuser')
        self.assertEqual(self.booking.car.model, 'Camry')
        self.assertEqual(self.booking.status, 'pending')
        self.assertEqual(self.booking.total_cost, 210.00)
    
    def test_booking_duration_days(self):
        """测试预订天数计算"""
        self.assertEqual(self.booking.duration_days(), 3)
    
    def test_driver_creation(self):
        """测试驾驶员对象创建"""
        self.assertEqual(self.driver.booking, self.booking)
        self.assertEqual(self.driver.get_full_name(), 'John Doe')
        self.assertTrue(self.driver.is_primary)
    
    def test_booking_options_cost(self):
        """测试预订选项成本计算"""
        # 启用附加选项
        self.booking.damage_waiver = True
        self.booking.satellite_navigation = True
        self.booking.child_seats = 2
        self.booking.save()
        
        # 根据预期计算公式验证结果
        expected_cost = 0  # 这里需要根据实际业务逻辑计算预期结果
        # 例如：每天15元的损坏豁免 + 每天10元的导航 + 每个儿童座椅每天5元
        expected_cost += 15 * 3  # 损坏豁免费用
        expected_cost += 10 * 3  # 导航费用
        expected_cost += 2 * 5 * 3  # 两个儿童座椅费用
        
        self.assertEqual(self.booking.options_cost(), expected_cost)
```

### 表单测试

```python
# accounts/tests/test_forms.py
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.forms import UserRegistrationForm, ProfileUpdateForm
from datetime import date

class UserRegistrationFormTest(TestCase):
    def test_valid_registration_form(self):
        """测试有效的注册表单"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_registration_form_passwords_mismatch(self):
        """测试密码不匹配的情况"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpassword123',
            'password2': 'differentpassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_invalid_registration_form_username_exists(self):
        """测试用户名已存在的情况"""
        # 创建已存在的用户
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpassword'
        )
        
        form_data = {
            'username': 'existinguser',  # 使用已存在的用户名
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class ProfileUpdateFormTest(TestCase):
    def test_valid_profile_update_form(self):
        """测试有效的个人资料更新表单"""
        form_data = {
            'phone': '0412345678',
            'address': '123 Main St, Sydney',
            'date_of_birth': date(1990, 5, 15),
            'license_number': 'DL98765432',
        }
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_future_date_of_birth(self):
        """测试未来出生日期的情况（如果有此验证）"""
        future_date = date.today().replace(year=date.today().year + 1)
        form_data = {
            'phone': '0412345678',
            'address': '123 Main St, Sydney',
            'date_of_birth': future_date,
            'license_number': 'DL98765432',
        }
        
        # 注意：以下测试假设表单中有对未来日期的验证
        # 如果没有此验证，测试可能会通过
        form = ProfileUpdateForm(data=form_data)
        if 'date_of_birth' in form.fields and hasattr(form, 'clean_date_of_birth'):
            self.assertFalse(form.is_valid())
            self.assertIn('date_of_birth', form.errors)
```

### 视图测试

```python
# cars/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from cars.models import Car, CarCategory

class CarListViewTest(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建汽车类别
        self.category = CarCategory.objects.create(
            name='Economy',
            description='Economical and fuel-efficient cars'
        )
        
        # 创建多个测试车辆
        self.car1 = Car.objects.create(
            make='Toyota',
            model='Yaris',
            year=2022,
            category='economy',
            daily_rate=50.00,
            transmission='automatic',
            fuel_type='gasoline',
            seats=5,
            luggage_capacity=2,
            air_conditioning=True,
            is_available=True,
            image='cars/yaris.jpg'
        )
        
        self.car2 = Car.objects.create(
            make='Honda',
            model='Civic',
            year=2023,
            category='comfort',
            daily_rate=65.00,
            transmission='automatic',
            fuel_type='gasoline',
            seats=5,
            luggage_capacity=3,
            air_conditioning=True,
            is_available=True,
            image='cars/civic.jpg'
        )
        
        self.car3 = Car.objects.create(
            make='BMW',
            model='X5',
            year=2023,
            category='luxury',
            daily_rate=120.00,
            transmission='automatic',
            fuel_type='diesel',
            seats=7,
            luggage_capacity=5,
            air_conditioning=True,
            is_available=True,
            image='cars/bmw_x5.jpg'
        )
    
    def test_car_list_view(self):
        """测试车辆列表视图"""
        response = self.client.get(reverse('car_list'))
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查所有车辆是否在响应中
        self.assertContains(response, 'Toyota Yaris')
        self.assertContains(response, 'Honda Civic')
        self.assertContains(response, 'BMW X5')
        
        # 检查模板使用
        self.assertTemplateUsed(response, 'cars/car_list.html')
    
    def test_car_filter_by_category(self):
        """测试按类别筛选车辆"""
        response = self.client.get(f"{reverse('car_list')}?category=luxury")
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查是否只包含奢华类别的车辆
        self.assertNotContains(response, 'Toyota Yaris')
        self.assertNotContains(response, 'Honda Civic')
        self.assertContains(response, 'BMW X5')
    
    def test_car_search(self):
        """测试车辆搜索功能"""
        response = self.client.get(f"{reverse('car_list')}?search=civic")
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查是否只包含搜索词匹配的车辆
        self.assertNotContains(response, 'Toyota Yaris')
        self.assertContains(response, 'Honda Civic')
        self.assertNotContains(response, 'BMW X5')
    
    def test_car_detail_view(self):
        """测试车辆详情视图"""
        response = self.client.get(reverse('car_detail', args=[self.car1.id]))
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查是否包含车辆详细信息
        self.assertContains(response, 'Toyota Yaris')
        self.assertContains(response, '$50.00')
        self.assertContains(response, '2022')
        
        # 检查模板使用
        self.assertTemplateUsed(response, 'cars/car_detail.html')
```

### 使用 pytest 的测试示例

```python
# tests/test_bookings.py
import pytest
from django.contrib.auth.models import User
from bookings.models import Booking
from cars.models import Car
from locations.models import Location
from datetime import date, timedelta

@pytest.fixture
def user():
    """创建测试用户"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )

@pytest.fixture
def locations():
    """创建测试地点"""
    pickup = Location.objects.create(
        name='Sydney Airport',
        address='Sydney International Airport',
        city='Sydney',
        state='NSW',
        country='Australia',
        latitude=-33.9399,
        longitude=151.1753
    )
    
    dropoff = Location.objects.create(
        name='Melbourne CBD',
        address='Melbourne Central',
        city='Melbourne',
        state='VIC',
        country='Australia',
        latitude=-37.8136,
        longitude=144.9631
    )
    
    return {'pickup': pickup, 'dropoff': dropoff}

@pytest.fixture
def car():
    """创建测试车辆"""
    return Car.objects.create(
        make='Toyota',
        model='Camry',
        year=2023,
        category='comfort',
        daily_rate=70.00,
        transmission='automatic',
        fuel_type='gasoline',
        seats=5,
        luggage_capacity=3,
        air_conditioning=True,
        is_available=True,
        image='cars/camry.jpg'
    )

@pytest.mark.django_db
def test_create_booking(user, car, locations):
    """测试创建预订"""
    today = date.today()
    booking = Booking.objects.create(
        user=user,
        car=car,
        pickup_location=locations['pickup'],
        dropoff_location=locations['dropoff'],
        pickup_date=today,
        return_date=today + timedelta(days=3),
        driver_age=30,
        status='pending',
        total_cost=210.00
    )
    
    assert booking.user == user
    assert booking.car == car
    assert booking.pickup_location == locations['pickup']
    assert booking.dropoff_location == locations['dropoff']
    assert booking.status == 'pending'
    assert booking.total_cost == 210.00
    assert booking.duration_days() == 3

@pytest.mark.django_db
def test_booking_options(user, car, locations):
    """测试预订选项"""
    today = date.today()
    booking = Booking.objects.create(
        user=user,
        car=car,
        pickup_location=locations['pickup'],
        dropoff_location=locations['dropoff'],
        pickup_date=today,
        return_date=today + timedelta(days=2),
        driver_age=30,
        status='pending',
        total_cost=140.00,
        damage_waiver=True,
        satellite_navigation=True
    )
    
    # 验证包含选项的预订
    assert booking.damage_waiver == True
    assert booking.satellite_navigation == True
    assert booking.child_seats == 0  # 默认值
    
    # 如果有计算选项成本的方法，也可以测试
    options_cost = booking.options_cost()
    assert isinstance(options_cost, (int, float))  # 确保返回数值
```

## 三、集成测试

### 预订流程集成测试

```python
# tests/test_booking_flow.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bookings.models import Booking, Driver
from cars.models import Car
from locations.models import Location
from datetime import date, timedelta
import uuid

class BookingFlowTest(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        
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
            is_available=True
        )
        
        # 登录用户
        self.client.login(username='testuser', password='testpassword')
    
    def test_complete_booking_flow(self):
        """测试完整的预订流程"""
        # 步骤1: 创建预订
        today = date.today()
        response = self.client.post(reverse('create_booking', args=[self.car.id]), {
            'pickup_location': self.pickup_location.id,
            'dropoff_location': self.dropoff_location.id,
            'pickup_date': today.strftime('%Y-%m-%d'),
            'return_date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            'driver_age': 30
        })
        
        # 检查重定向到驾驶员信息页面
        self.assertEqual(response.status_code, 302)
        
        # 从会话中获取临时预订ID
        session = self.client.session
        temp_booking_id = None
        for key in session.keys():
            if key.startswith('temp_booking_'):
                temp_booking_id = key.split('_')[-1]
                break
        
        self.assertIsNotNone(temp_booking_id)
        
        # 步骤2: 添加驾驶员信息
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
        
        response = self.client.post(reverse('add_drivers', args=[temp_booking_id]), driver_data)
        
        # 检查重定向到选项页面
        self.assertEqual(response.status_code, 302)
        self.assertIn('add_options', response.url)
        
        # 步骤3: 添加选项
        options_data = {
            'damage_waiver': 'on',
            'satellite_navigation': 'on',
            'child_seats': 1
        }
        
        response = self.client.post(reverse('add_options', args=[temp_booking_id]), options_data)
        
        # 检查重定向到确认页面
        self.assertEqual(response.status_code, 302)
        self.assertIn('confirm_booking', response.url)
        
        # 步骤4: 确认预订
        response = self.client.post(reverse('confirm_booking', args=[temp_booking_id]), {
            'confirm': 'true'
        })
        
        # 检查重定向到支付页面
        self.assertEqual(response.status_code, 302)
        self.assertIn('payment', response.url)
        
        # 步骤5: 处理支付（模拟）
        response = self.client.post(reverse('process_payment', args=[temp_booking_id]), {
            'payment_method': 'card',
            'simulate_success': 'true'  # 假设有一个用于测试的标志
        })
        
        # 检查重定向到支付成功页面
        self.assertEqual(response.status_code, 302)
        self.assertIn('payment_success', response.url)
        
        # 验证数据库中的预订记录
        booking = Booking.objects.filter(user=self.user).last()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.car, self.car)
        self.assertEqual(booking.status, 'confirmed')  # 假设支付成功后状态为"已确认"
        self.assertEqual(booking.pickup_location, self.pickup_location)
        self.assertEqual(booking.dropoff_location, self.dropoff_location)
        
        # 验证驾驶员信息
        driver = Driver.objects.filter(booking=booking).first()
        self.assertIsNotNone(driver)
        self.assertEqual(driver.first_name, 'John')
        self.assertEqual(driver.last_name, 'Doe')
        self.assertEqual(driver.email, 'john.doe@example.com')
        self.assertTrue(driver.is_primary)
```

### 用户注册和认证测试

```python
# tests/test_auth.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile

class UserAuthenticationTest(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpassword'
        )
        
        # 确保用户有关联的个人资料
        Profile.objects.get_or_create(user=self.user)
    
    def test_user_registration(self):
        """测试用户注册流程"""
        # 提交注册表单
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        
        # 检查重定向到登录页面
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # 验证用户是否创建成功
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # 验证个人资料是否创建
        new_user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(new_user, 'profile'))
    
    def test_user_login(self):
        """测试用户登录"""
        # 提交登录表单
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'testpassword',
        })
        
        # 检查重定向到首页
        self.assertEqual(response.status_code, 302)
        
        # 验证用户是否已登录
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_user_login_invalid_credentials(self):
        """测试无效凭据登录"""
        # 提交错误密码的登录表单
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'wrongpassword',
        })
        
        # 检查是否显示错误消息
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_user_logout(self):
        """测试用户登出"""
        # 先登录
        self.client.login(username='existinguser', password='testpassword')
        
        # 发送登出请求
        response = self.client.get(reverse('logout'))
        
        # 检查重定向到登录页面或首页
        self.assertEqual(response.status_code, 302)
        
        # 验证用户已登出
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_profile_view_authenticated(self):
        """测试已认证用户访问个人资料页面"""
        # 先登录
        self.client.login(username='existinguser', password='testpassword')
        
        # 访问个人资料页面
        response = self.client.get(reverse('profile'))
        
        # 检查页面是否成功加载
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
    
    def test_profile_view_unauthenticated(self):
        """测试未认证用户访问个人资料页面"""
        # 未登录用户尝试访问个人资料页面
        response = self.client.get(reverse('profile'))
        
        # 检查是否重定向到登录页面
        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')
        self.assertTrue(login_url in response.url)
```

## 四、功能测试（使用 Selenium）

```python
# tests/functional_tests.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from cars.models import Car
from locations.models import Location
import time

class BookingFunctionalTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        """设置测试浏览器"""
        super().setUpClass()
        
        # 设置无头Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        """清理测试浏览器"""
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        """设置测试数据"""
        # 创建用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # 创建地点
        self.location = Location.objects.create(
            name='Sydney, NSW',
            address='Sydney, Australia',
            city='Sydney',
            state='NSW',
            country='Australia'
        )
        
        # 创建多个车辆
        self.car1 = Car.objects.create(
            make='Toyota',
            model='Corolla',
            year=2023,
            category='economy',
            daily_rate=55.00,
            is_available=True
        )
        
        self.car2 = Car.objects.create(
            make='Honda',
            model='Accord',
            year=2023,
            category='comfort',
            daily_rate=75.00,
            is_available=True
        )
    
    def test_search_and_book_car(self):
        """测试搜索车辆和开始预订流程"""
        # 访问首页
        self.selenium.get(f"{self.live_server_url}/")
        
        # 等待页面加载
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hero-section"))
        )
        
        # 填写搜索表单
        try:
            # 选择地点
            location_select = self.selenium.find_element(By.NAME, "pickup_location")
            location_select.send_keys("Sydney")
            
            # 选择日期
            pickup_date = self.selenium.find_element(By.NAME, "pickup_date")
            pickup_date.clear()
            pickup_date.send_keys("10-06-2023")
            
            return_date = self.selenium.find_element(By.NAME, "return_date")
            return_date.clear()
            return_date.send_keys("15-06-2023")
            
            # 提交表单
            search_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            
            # 等待结果页面加载
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "car-list"))
            )
            
            # 验证结果页面
            self.assertIn("Car Rental", self.selenium.title)
            
            # 选择一个车辆
            car_link = self.selenium.find_element(By.CSS_SELECTOR, ".car-card a.btn-primary")
            car_link.click()
            
            # 等待详情页面加载
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "car-detail"))
            )
            
            # 点击预订按钮
            book_button = self.selenium.find_element(By.CSS_SELECTOR, "form button[type='submit']")
            book_button.click()
            
            # 因为未登录，应重定向到登录页面
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.ID, "login-form"))
            )
            
            # 登录
            username_input = self.selenium.find_element(By.NAME, "username")
            password_input = self.selenium.find_element(By.NAME, "password")
            
            username_input.send_keys("testuser")
            password_input.send_keys("testpassword")
            
            login_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # 登录后应重定向到驾驶员信息页面
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form .driver-form"))
            )
            
            # 验证页面标题
            self.assertIn("Driver Information", self.selenium.title)
            
        except TimeoutException as e:
            # 截图以便调试
            self.selenium.save_screenshot('test_failure.png')
            raise e
```

## 五、性能测试

### 使用 locust 进行负载测试

```python
# locustfile.py
from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # 用户请求之间等待1-5秒
    
    def on_start(self):
        """用户开始前的操作，例如登录"""
        self.login()
    
    def login(self):
        """用户登录"""
        response = self.client.get("/accounts/login/")
        csrftoken = response.cookies.get('csrftoken')
        
        self.client.post("/accounts/login/", {
            'username': 'testuser',
            'password': 'testpassword',
            'csrfmiddlewaretoken': csrftoken
        })
    
    @task(3)
    def view_homepage(self):
        """访问首页"""
        self.client.get("/")
    
    @task(2)
    def view_car_list(self):
        """查看车辆列表"""
        self.client.get("/cars/")
    
    @task(1)
    def view_random_car(self):
        """查看随机车辆详情"""
        # 假设有10辆车
        car_id = random.randint(1, 10)
        self.client.get(f"/cars/{car_id}/")
    
    @task(1)
    def search_cars(self):
        """搜索车辆"""
        pickup_locations = ["Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD"]
        pickup_location = random.choice(pickup_locations)
        
        self.client.get(f"/cars/?pickup_location={pickup_location}&pickup_date=2023-06-10&return_date=2023-06-15")
```

## 六、测试覆盖率分析

### 使用 coverage.py 分析测试覆盖率

```bash
# 运行测试并收集覆盖率数据
coverage run --source='.' manage.py test

# 生成覆盖率报告
coverage report -m

# 生成HTML覆盖率报告
coverage html
```

### 配置 .coveragerc 文件

```ini
# .coveragerc
[run]
source = .
omit =
    */migrations/*
    */tests/*
    */test_*.py
    */manage.py
    */settings.py
    */wsgi.py
    */asgi.py
    venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError
```

## 七、持续集成测试

### GitHub Actions 配置示例

```yaml
# .github/workflows/django-tests.yml
name: Django Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 4
      matrix:
        python-version: [3.11]

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run Tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        RUSH_ENVIRONMENT: testing
      run: |
        python manage.py test
    
    - name: Run Pytest
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        RUSH_ENVIRONMENT: testing
      run: |
        pytest
    
    - name: Generate Coverage Report
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        RUSH_ENVIRONMENT: testing
      run: |
        coverage run --source='.' manage.py test
        coverage xml
    
    - name: Upload Coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

## 八、安全测试

### 使用 django-security 进行安全检查

```bash
# 安装 django-security
pip install django-security

# 运行安全检查
python manage.py checksecure
```

### 使用 Bandit 进行静态安全分析

```bash
# 安装 bandit
pip install bandit

# 运行安全扫描
bandit -r .
```

## 九、测试最佳实践

1. **保持测试独立性**：每个测试应该独立运行，不依赖于其他测试的状态。

2. **使用测试数据库**：测试应该在隔离的测试数据库中运行，不影响开发或生产数据。

3. **模拟外部服务**：使用 mock 或 stub 来模拟外部服务，如支付网关。

4. **测试边界条件**：除了测试正常路径外，还应测试边界条件和错误情况。

5. **代码覆盖率**：尽量达到高代码覆盖率，特别是关键业务逻辑。

6. **定期运行测试**：在CI/CD流程中自动运行测试，确保每次提交都通过测试。

7. **维护测试代码**：像维护应用代码一样维护测试代码，保持其可读性和可维护性。

8. **优先测试核心功能**：优先测试核心业务逻辑和关键用户流程。

## 十、测试计划执行

### 测试环境配置

1. **开发环境**：开发人员本地测试
2. **CI环境**：自动化测试
3. **QA环境**：手动测试和验收测试
4. **预生产环境**：性能测试和最终验收

### 测试执行顺序

1. 单元测试
2. 集成测试
3. 功能测试
4. 性能测试
5. 安全测试

### 测试通过标准

1. 所有自动化测试通过
2. 代码覆盖率达到指定阈值（如80%）
3. 无高级别或中级别安全漏洞
4. 性能指标满足要求

## 结论

本测试指南提供了 Rush Car Rental 项目的全面测试策略。通过实施这些测试，可以确保系统的稳定性、可靠性和安全性。测试应该被视为开发过程的核心部分，而不是一个附加活动。通过持续测试和监控，可以及早发现并解决问题，提供更好的用户体验。