from django.test import TestCase
from cars.models import Car


class CarModelTest(TestCase):
    """
    测试 Car 模型的基本功能
    """

    def setUp(self):
        """
        初始化测试数据
        """
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

    def test_car_creation(self):
        """
        测试车辆创建和基本属性
        """
        self.assertEqual(self.car.make, 'Toyota')
        self.assertEqual(self.car.model, 'Camry')
        self.assertEqual(self.car.year, 2023)
        self.assertEqual(self.car.category, 'comfort')
        self.assertEqual(self.car.daily_rate, 70.00)
        self.assertTrue(self.car.is_available)

    def test_car_string_representation(self):
        """
        测试车辆的字符串表示
        """
        expected_string = f"{self.car.year} {self.car.make} {self.car.model}"
        self.assertEqual(str(self.car), expected_string)

    def test_car_availability(self):
        """
        测试车辆可用性切换
        """
        self.assertTrue(self.car.is_available)
        
        # 将车辆设为不可用
        self.car.is_available = False
        self.car.save()
        
        # 重新从数据库加载
        updated_car = Car.objects.get(id=self.car.id)
        self.assertFalse(updated_car.is_available)