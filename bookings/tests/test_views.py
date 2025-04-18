from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from bookings.models import Booking, Driver
from bookings.views import MockStripe
from cars.models import Car
from locations.models import Location
from accounts.models import Profile


class BookingViewsTest(TestCase):
    """
    测试预订相关视图
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
            status='confirmed',
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
    
    def test_create_booking_view_unauthenticated(self):
        """
        测试未认证用户访问创建预订页面
        """
        response = self.client.get(reverse('create_booking', args=[self.car.id]))
        
        # 应该重定向到登录页面
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)
    
    def test_create_booking_view_authenticated(self):
        """
        测试已认证用户访问创建预订页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('create_booking', args=[self.car.id]))
        
        # 应该显示创建预订页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/create_booking.html')
        
        # 检查上下文是否包含车辆
        self.assertEqual(response.context['car'], self.car)
    
    def test_create_booking_view_post_valid(self):
        """
        测试有效的创建预订 POST 请求
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        # 明天和一周后的日期
        tomorrow = self.today + timedelta(days=1)
        next_week = self.today + timedelta(days=7)
        
        response = self.client.post(reverse('create_booking', args=[self.car.id]), {
            'pickup_location': self.pickup_location.id,
            'dropoff_location': self.dropoff_location.id,
            'pickup_date': tomorrow.strftime('%Y-%m-%d'),
            'return_date': next_week.strftime('%Y-%m-%d'),
            'driver_age': 30
        })
        
        # 应该重定向到驾驶员信息页面
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/drivers/' in response.url)
        
        # 从重定向URL中提取临时预订ID
        temp_booking_id = response.url.split('/')[-2]
        
        # 检查会话是否包含临时预订
        session_key = f'temp_booking_{temp_booking_id}'
        self.assertIn(session_key, self.client.session)
    
    def test_booking_detail_view_authenticated(self):
        """
        测试已认证用户访问预订详情页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('booking_detail', args=[self.booking.id]))
        
        # 应该显示预订详情页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_detail.html')
        
        # 检查上下文是否包含预订
        self.assertEqual(response.context['booking'], self.booking)
    
    def test_booking_detail_view_wrong_user(self):
        """
        测试用户访问不属于自己的预订详情页面
        """
        # 创建另一个用户
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpassword'
        )
        
        # 用其他用户登录
        self.client.login(username='otheruser', password='testpassword')
        
        response = self.client.get(reverse('booking_detail', args=[self.booking.id]))
        
        # 应该返回 404 或重定向到其他页面，具体取决于视图实现
        self.assertNotEqual(response.status_code, 200)
    
    def test_cancel_booking_view_authenticated(self):
        """
        测试已认证用户访问取消预订页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('cancel_booking', args=[self.booking.id]))
        
        # 应该显示取消预订页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/cancel_booking.html')
    
    def test_cancel_booking_view_post_valid(self):
        """
        测试有效的取消预订 POST 请求
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.post(reverse('cancel_booking', args=[self.booking.id]), {
            'cancel_reason': 'change_of_plans',
            'comments': 'Need to reschedule.'
        })
        
        # 应该重定向到预订列表页面
        self.assertEqual(response.status_code, 302)
        
        # 刷新预订
        self.booking.refresh_from_db()
        
        # 检查预订状态是否已更改为已取消
        self.assertEqual(self.booking.status, 'cancelled')
    
    def test_payment_success_view_authenticated(self):
        """
        测试已认证用户访问支付成功页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('payment_success', args=[self.booking.id]))
        
        # 应该显示支付成功页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/payment_success.html')
    
    def test_booking_success_view_authenticated(self):
        """
        测试已认证用户访问预订成功页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('booking_success', args=[self.booking.id]))
        
        # 应该显示预订成功页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_success.html')


class MockStripeTest(TestCase):
    """
    测试模拟 Stripe 功能
    """
    
    def test_payment_intent_create(self):
        """
        测试创建支付意向
        """
        payment_intent = MockStripe.PaymentIntent.create(
            amount=10000,
            currency='usd',
            payment_method_types=['card']
        )
        
        self.assertIn('id', payment_intent)
        self.assertIn('client_secret', payment_intent)
        self.assertEqual(payment_intent['amount'], 10000)
        self.assertEqual(payment_intent['currency'], 'usd')
        self.assertEqual(payment_intent['status'], 'requires_payment_method')
    
    def test_payment_intent_retrieve(self):
        """
        测试检索支付意向
        """
        # 创建支付意向
        payment_intent = MockStripe.PaymentIntent.create(
            amount=10000,
            currency='usd',
            payment_method_types=['card']
        )
        
        # 检索支付意向
        retrieved_intent = MockStripe.PaymentIntent.retrieve(payment_intent['id'])
        
        self.assertEqual(retrieved_intent['id'], payment_intent['id'])
        self.assertEqual(retrieved_intent['amount'], payment_intent['amount'])
    
    def test_checkout_session_create(self):
        """
        测试创建结账会话
        """
        session = MockStripe.checkout.Session.create(
            line_items=[{'price': 'price_123', 'quantity': 1}],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )
        
        self.assertIn('id', session)
        self.assertIn('url', session)
        self.assertEqual(session['mode'], 'payment')
    
    def test_checkout_session_retrieve(self):
        """
        测试检索结账会话
        """
        # 创建结账会话
        session = MockStripe.checkout.Session.create(
            line_items=[{'price': 'price_123', 'quantity': 1}],
            mode='payment',
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel'
        )
        
        # 检索结账会话
        retrieved_session = MockStripe.checkout.Session.retrieve(session['id'])
        
        self.assertEqual(retrieved_session['id'], session['id'])
        self.assertEqual(retrieved_session['mode'], session['mode'])