from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from accounts.models import Profile
from bookings.models import Driver


class AccountViewsTest(TestCase):
    """
    测试账户相关视图
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
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        
        # 确保用户有关联的个人资料
        self.profile = Profile.objects.get_or_create(user=self.user)[0]
        
        # 创建测试驾驶员
        self.driver = Driver.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            date_of_birth=date(1990, 1, 15),
            license_number='DL12345678',
            license_issued_in='NSW',
            license_expiry_date=date.today(),
            address='123 Test Street',
            city='Sydney',
            state='NSW',
            postcode='2000',
            country_of_residence='Australia',
            mobile='0400123456',
            is_primary=True
        )
        
        # 将驾驶员添加到用户个人资料
        self.profile.drivers.add(self.driver)
    
    def test_register_view_get(self):
        """
        测试注册页面 GET 请求
        """
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_view_post_valid(self):
        """
        测试有效的注册 POST 请求
        """
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        })
        
        # 应该重定向到登录页面
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # 检查用户是否创建成功
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_view_post_invalid(self):
        """
        测试无效的注册 POST 请求
        """
        response = self.client.post(reverse('register'), {
            'username': '',  # 空用户名
            'email': 'invalid-email',  # 无效邮箱
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'password',  # 过于简单的密码
            'password2': 'different',  # 不匹配的密码
        })
        
        # 应该返回表单错误，状态码仍为 200
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        
        # 检查表单中是否包含错误
        self.assertTrue(response.context['form'].errors)
    
    def test_profile_view_unauthenticated(self):
        """
        测试未认证用户访问个人资料页面
        """
        response = self.client.get(reverse('profile'))
        
        # 应该重定向到登录页面
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/login/' in response.url)
    
    def test_profile_view_authenticated(self):
        """
        测试已认证用户访问个人资料页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('profile'))
        
        # 应该显示个人资料页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
        # 检查个人资料是否在上下文中
        self.assertEqual(response.context['u_form'].instance, self.user)
        self.assertEqual(response.context['p_form'].instance, self.profile)
    
    def test_profile_view_post_valid(self):
        """
        测试有效的个人资料更新 POST 请求
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.post(reverse('profile'), {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone': '0412345678',
            'address': '123 Main St, Sydney',
            'date_of_birth': '1990-05-15',
            'license_number': 'DL98765432',
        })
        
        # 应该重定向回个人资料页面
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # 刷新用户和个人资料
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        # 检查更新是否成功
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.profile.phone, '0412345678')
        self.assertEqual(self.profile.license_number, 'DL98765432')
    
    def test_add_driver_view_authenticated(self):
        """
        测试已认证用户访问添加驾驶员页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('add_driver'))
        
        # 应该显示添加驾驶员页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/driver_form.html')
    
    def test_add_driver_view_post_valid(self):
        """
        测试有效的添加驾驶员 POST 请求
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        # 初始驾驶员数量
        initial_driver_count = self.profile.drivers.count()
        
        response = self.client.post(reverse('add_driver'), {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'date_of_birth': '1992-05-20',
            'license_number': 'DL87654321',
            'license_issued_in': 'VIC',
            'license_expiry_date': '2025-01-01',
            'address': '456 Test Street',
            'city': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'country_of_residence': 'Australia',
            'mobile': '0400654321',
            'is_primary': '',  # 不是主驾驶员
        })
        
        # 应该重定向回个人资料页面
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # 刷新个人资料
        self.profile.refresh_from_db()
        
        # 检查是否添加了新驾驶员
        self.assertEqual(self.profile.drivers.count(), initial_driver_count + 1)
        
        # 检查新驾驶员的信息
        new_driver = self.profile.drivers.exclude(id=self.driver.id).first()
        self.assertEqual(new_driver.first_name, 'Jane')
        self.assertEqual(new_driver.last_name, 'Doe')
        self.assertEqual(new_driver.email, 'jane.doe@example.com')
        self.assertFalse(new_driver.is_primary)
    
    def test_edit_driver_view_authenticated(self):
        """
        测试已认证用户访问编辑驾驶员页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('edit_driver', args=[self.driver.id]))
        
        # 应该显示编辑驾驶员页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/driver_form.html')
        
        # 检查表单是否包含正确的驾驶员信息
        self.assertEqual(response.context['form'].instance, self.driver)
    
    def test_edit_driver_view_post_valid(self):
        """
        测试有效的编辑驾驶员 POST 请求
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.post(reverse('edit_driver', args=[self.driver.id]), {
            'first_name': 'John',
            'last_name': 'Smith',  # 更改姓氏
            'email': 'john.smith@example.com',  # 更改邮箱
            'date_of_birth': '1990-01-15',
            'license_number': 'DL12345678',
            'license_issued_in': 'NSW',
            'license_expiry_date': '2025-01-01',
            'address': '123 Test Street',
            'city': 'Sydney',
            'state': 'NSW',
            'postcode': '2000',
            'country_of_residence': 'Australia',
            'mobile': '0400123456',
            'is_primary': 'on',  # 仍然是主驾驶员
        })
        
        # 应该重定向回个人资料页面
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # 刷新驾驶员
        self.driver.refresh_from_db()
        
        # 检查更新是否成功
        self.assertEqual(self.driver.last_name, 'Smith')
        self.assertEqual(self.driver.email, 'john.smith@example.com')
        self.assertTrue(self.driver.is_primary)
    
    def test_delete_driver_view_authenticated(self):
        """
        测试已认证用户访问删除驾驶员页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('delete_driver', args=[self.driver.id]))
        
        # 应该显示确认删除页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/confirm_delete_driver.html')
    
    def test_delete_driver_view_post(self):
        """
        测试删除驾驶员 POST 请求
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        # 初始驾驶员数量
        initial_driver_count = self.profile.drivers.count()
        
        response = self.client.post(reverse('delete_driver', args=[self.driver.id]))
        
        # 应该重定向回个人资料页面
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # 刷新个人资料
        self.profile.refresh_from_db()
        
        # 检查是否删除了驾驶员
        self.assertEqual(self.profile.drivers.count(), initial_driver_count - 1)
        self.assertFalse(Driver.objects.filter(id=self.driver.id).exists())
    
    def test_user_bookings_view_authenticated(self):
        """
        测试已认证用户访问我的预订页面
        """
        # 登录
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(reverse('user_bookings'))
        
        # 应该显示我的预订页面
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user_bookings.html')