from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from accounts.models import Profile
from bookings.models import Driver


class ProfileModelTest(TestCase):
    """
    测试 Profile 模型的基本功能
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
        
        # 确保 Profile 自动创建
        self.profile = self.user.profile
        
        # 手动更新一些字段
        self.profile.phone = '0412345678'
        self.profile.address = '123 Test Street, Sydney'
        self.profile.date_of_birth = date(1990, 1, 15)
        self.profile.license_number = 'DL98765432'
        self.profile.save()

    def test_profile_creation(self):
        """
        测试个人资料创建和基本属性
        """
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone, '0412345678')
        self.assertEqual(self.profile.address, '123 Test Street, Sydney')
        self.assertEqual(self.profile.date_of_birth, date(1990, 1, 15))
        self.assertEqual(self.profile.license_number, 'DL98765432')

    def test_profile_string_representation(self):
        """
        测试个人资料的字符串表示
        """
        expected_string = f"{self.user.username}'s profile"
        self.assertEqual(str(self.profile), expected_string)

    def test_profile_driver_relationship(self):
        """
        测试个人资料与驾驶员的关系
        """
        # 创建测试驾驶员
        driver1 = Driver.objects.create(
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
        
        driver2 = Driver.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            date_of_birth=date(1992, 5, 20),
            license_number='DL87654321',
            license_issued_in='VIC',
            license_expiry_date=date.today(),
            address='456 Test Street',
            city='Melbourne',
            state='VIC',
            postcode='3000',
            country_of_residence='Australia',
            mobile='0400654321',
            is_primary=False
        )
        
        # 将驾驶员添加到个人资料
        self.profile.drivers.add(driver1)
        self.profile.drivers.add(driver2)
        
        # 验证关系
        self.assertEqual(self.profile.drivers.count(), 2)
        self.assertIn(driver1, self.profile.drivers.all())
        self.assertIn(driver2, self.profile.drivers.all())
        
        # 测试主驾驶员功能
        primary_driver = self.profile.get_primary_driver()
        self.assertEqual(primary_driver, driver1)
        
        # 更改主驾驶员
        driver1.is_primary = False
        driver1.save()
        driver2.is_primary = True
        driver2.save()
        
        # 重新测试
        primary_driver = self.profile.get_primary_driver()
        self.assertEqual(primary_driver, driver2)