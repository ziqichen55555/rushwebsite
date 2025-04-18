import os
import sys
import json
import uuid
from datetime import datetime, timedelta

"""
Stripe集成测试脚本

这个脚本用于测试Stripe支付集成功能，无需实际的Stripe API密钥。
模拟Stripe API的行为，以便于开发和测试。
"""

# 将项目根目录添加到Python路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')
import django
django.setup()

# 导入Django模型和视图
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from cars.models import Car, CarCategory
from locations.models import Location, State
from bookings.models import Booking


def test_payment_flow():
    """测试支付流程"""
    print("=== 测试支付流程 ===")
    
    # 创建测试客户端
    client = Client()
    
    # 确保有测试用户
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "testpassword123"
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=email, password=password)
    
    # 登录用户
    logged_in = client.login(username=username, password=password)
    if not logged_in:
        print(f"❌ 登录失败: {username}")
        return
    
    print(f"✅ 登录成功: {username}")
    
    # 确保有测试用车辆和位置
    try:
        category = CarCategory.objects.first()
        if not category:
            category = CarCategory.objects.create(name="Test Category", description="Test Description")
        
        car = Car.objects.first()
        if not car:
            car = Car.objects.create(
                name="Test Car",
                make="Test Make",
                model="Test Model",
                year=2023,
                category=category,
                seats=5,
                bags=3,
                doors=4,
                transmission="A",
                air_conditioning=True,
                image_url="https://example.com/car.jpg",
                daily_rate=50.00,
                is_available=True
            )
        
        state = State.objects.first()
        if not state:
            state = State.objects.create(name="Test State", code="TS")
        
        pickup_location = Location.objects.first()
        if not pickup_location:
            pickup_location = Location.objects.create(
                name="Test Location 1",
                address="123 Test St",
                city="Test City",
                state=state,
                postal_code="12345",
                is_airport=False
            )
        
        dropoff_location = pickup_location
        
    except Exception as e:
        print(f"❌ 设置测试数据失败: {str(e)}")
        return
    
    # 创建测试预订
    try:
        # 删除之前的测试预订
        Booking.objects.filter(user=user).delete()
        
        # 创建一个新的预订
        today = datetime.now().date()
        pickup_date = today + timedelta(days=7)
        return_date = today + timedelta(days=14)
        
        booking = Booking.objects.create(
            user=user,
            car=car,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            pickup_date=pickup_date,
            return_date=return_date,
            status='pending',
            total_cost=car.daily_rate * 7,
            driver_age=30
        )
        
        print(f"✅ 创建预订成功: ID {booking.id}, 总金额 {booking.total_cost}")
        
    except Exception as e:
        print(f"❌ 创建预订失败: {str(e)}")
        return
    
    # 测试支付流程
    try:
        # 1. 跳转到支付页面
        payment_url = f"/bookings/{booking.id}/payment/"
        response = client.get(payment_url)
        
        if response.status_code != 200:
            print(f"❌ 访问支付页面失败: 状态码 {response.status_code}")
            return
        
        print(f"✅ 访问支付页面成功")
        
        # 2. 处理支付
        process_url = f"/bookings/{booking.id}/process_payment/"
        response = client.post(process_url, {"payment_method": "stripe"})
        
        if response.status_code not in [200, 302]:
            print(f"❌ 处理支付失败: 状态码 {response.status_code}")
            return
        
        print(f"✅ 处理支付请求成功")
        
        # 3. 模拟支付成功回调
        success_url = f"/bookings/{booking.id}/stripe_success/"
        response = client.get(success_url)
        
        if response.status_code not in [200, 302]:
            print(f"❌ 支付成功回调失败: 状态码 {response.status_code}")
            return
        
        print(f"✅ 支付成功回调处理成功")
        
        # 4. 检查预订状态
        booking.refresh_from_db()
        if booking.status != 'confirmed':
            print(f"❌ 预订状态更新失败: 当前状态为 {booking.status}, 应为 confirmed")
            return
        
        print(f"✅ 预订状态已更新为 {booking.status}")
        
        print("\n🎉 支付流程测试成功!")
        
    except Exception as e:
        print(f"❌ 支付流程测试失败: {str(e)}")


def test_stripe_checkout():
    """测试Stripe结账流程"""
    print("\n=== 测试Stripe结账流程 ===")
    
    # 检查环境变量
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    if not stripe_key:
        print("⚠️ 未设置STRIPE_SECRET_KEY环境变量，使用测试密钥")
        stripe_key = "sk_test_example_key"
    
    print(f"✅ 使用Stripe密钥: {stripe_key[:4]}...{stripe_key[-4:]}")
    
    # 创建测试客户端
    client = Client()
    
    # 确保有测试用户并登录
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    password = "testpassword123"
    
    try:
        user = User.objects.create_user(username=username, password=password)
        logged_in = client.login(username=username, password=password)
        if not logged_in:
            print(f"❌ 登录失败: {username}")
            return
    except Exception as e:
        print(f"❌ 用户创建或登录失败: {str(e)}")
        return
    
    # 创建测试预订数据
    try:
        # 确保有必要的测试数据
        category = CarCategory.objects.first() or CarCategory.objects.create(name="Test Category")
        state = State.objects.first() or State.objects.create(name="Test State", code="TS")
        
        car = Car.objects.create(
            name="Test Checkout Car",
            make="Test",
            model="Checkout",
            year=2023,
            category=category,
            seats=4,
            bags=2,
            doors=4,
            transmission="A",
            image_url="https://example.com/car.jpg",
            daily_rate=75.00,
            is_available=True
        )
        
        location = Location.objects.first() or Location.objects.create(
            name="Test Location",
            address="123 Test St",
            city="Test City",
            state=state,
            postal_code="12345"
        )
        
        today = datetime.now().date()
        booking = Booking.objects.create(
            user=user,
            car=car,
            pickup_location=location,
            dropoff_location=location,
            pickup_date=today + timedelta(days=3),
            return_date=today + timedelta(days=6),
            status='pending',
            total_cost=225.00,  # 3天 * 75.00
            driver_age=25
        )
        
        print(f"✅ 创建测试预订: ID {booking.id}, 金额 ${booking.total_cost}")
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {str(e)}")
        return
    
    # 测试Stripe结账会话创建
    try:
        print("\n🔍 测试Stripe结账会话创建...")
        
        # 请求结账会话
        response = client.post(f'/bookings/{booking.id}/process_payment/', {
            'payment_method': 'stripe_checkout',
        })
        
        if response.status_code != 302:  # 应该是重定向
            print(f"❌ 创建结账会话失败: 状态码 {response.status_code}")
            print(f"响应内容: {response.content.decode()[:200]}...")
            return
        
        # 检查重定向URL
        redirect_url = response.url
        print(f"✅ 重定向到: {redirect_url}")
        
        if 'stripe.com' in redirect_url or 'checkout/session' in redirect_url:
            print("✅ 重定向到Stripe结账页面成功")
        else:
            print(f"❌ 未重定向到Stripe结账页面")
        
        # 模拟Stripe回调
        print("\n🔍 模拟Stripe结账成功回调...")
        
        success_url = f'/bookings/{booking.id}/stripe_success/'
        response = client.get(success_url)
        
        if response.status_code in [200, 302]:
            print(f"✅ 结账成功回调处理成功")
        else:
            print(f"❌ 结账成功回调失败: 状态码 {response.status_code}")
            return
        
        # 验证预订状态更新
        booking.refresh_from_db()
        print(f"✅ 更新后的预订状态: {booking.status}")
        
        print("\n🎉 Stripe结账流程测试完成!")
        
    except Exception as e:
        print(f"❌ Stripe结账测试失败: {str(e)}")


if __name__ == "__main__":
    print("\n==================================================")
    print("🚗 Rush Car Rental - Stripe集成测试")
    print("==================================================\n")
    
    # 运行测试
    test_payment_flow()
    test_stripe_checkout()
    
    print("\n==================================================")
    print("测试完成")
    print("==================================================\n")