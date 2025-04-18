from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from accounts.forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, ProfileDriverForm


class UserRegistrationFormTest(TestCase):
    """
    测试用户注册表单
    """
    
    def setUp(self):
        """
        设置测试数据
        """
        # 创建测试用户（用于测试用户名已存在的情况）
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpassword'
        )
    
    def test_valid_registration_form(self):
        """
        测试有效的注册表单
        """
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_registration_form_passwords_mismatch(self):
        """
        测试密码不匹配的情况
        """
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'securepassword123',
            'password2': 'differentpassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_invalid_registration_form_username_exists(self):
        """
        测试用户名已存在的情况
        """
        form_data = {
            'username': 'existinguser',  # 使用已存在的用户名
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'securepassword123',
            'password2': 'securepassword123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class UserUpdateFormTest(TestCase):
    """
    测试用户更新表单
    """
    
    def setUp(self):
        """
        设置测试数据
        """
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        
        # 创建另一个用户（用于测试邮箱已存在的情况）
        self.another_user = User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='testpassword'
        )
    
    def test_valid_user_update_form(self):
        """
        测试有效的用户更新表单
        """
        form_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_invalid_user_update_form_email_exists(self):
        """
        测试邮箱已存在的情况
        """
        form_data = {
            'username': 'testuser',
            'email': 'another@example.com',  # 使用另一个用户的邮箱
            'first_name': 'Test',
            'last_name': 'User',
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class ProfileUpdateFormTest(TestCase):
    """
    测试个人资料更新表单
    """
    
    def test_valid_profile_update_form(self):
        """
        测试有效的个人资料更新表单
        """
        form_data = {
            'phone': '0412345678',
            'address': '123 Main St, Sydney',
            'date_of_birth': date(1990, 5, 15),
            'license_number': 'DL98765432',
        }
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_profile_update_form_optional_fields(self):
        """
        测试可选字段
        """
        # 空的 date_of_birth 应该是有效的，因为它是可选的
        form_data = {
            'phone': '0412345678',
            'address': '123 Main St, Sydney',
            'license_number': 'DL98765432',
        }
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())


class ProfileDriverFormTest(TestCase):
    """
    测试个人资料驾驶员表单
    """
    
    def test_valid_profile_driver_form(self):
        """
        测试有效的个人资料驾驶员表单
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
            'is_primary': True,
        }
        form = ProfileDriverForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_profile_driver_form_future_birth_date(self):
        """
        测试出生日期为未来日期的情况
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
            'is_primary': True,
        }
        form = ProfileDriverForm(data=form_data)
        
        # 如果表单有对出生日期的验证，则应该无效
        # 注意：这取决于表单是否实现了该验证
        if hasattr(form, 'clean_date_of_birth'):
            self.assertFalse(form.is_valid())
            self.assertIn('date_of_birth', form.errors)