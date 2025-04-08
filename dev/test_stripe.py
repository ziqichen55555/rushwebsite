#!/usr/bin/env python
"""
Stripe集成测试脚本

这个脚本用于测试Stripe支付集成功能，无需实际的Stripe API密钥。
模拟Stripe API的行为，以便于开发和测试。
"""

import os
import sys
import uuid
import json
from decimal import Decimal

# 添加项目根目录到sys.path
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')

# 设置Django
import django
django.setup()

# 导入必要的模块
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from bookings.models import Booking
from cars.models import Car, CarCategory
from locations.models import Location, State

# 打印系统信息
print("===== Rush Car Rental - Stripe集成测试 =====")
print(f"Django版本: {django.get_version()}")
print(f"测试时间: {django.utils.timezone.now()}")
print("=" * 50)

# 创建一个测试客户端
client = Client()

# 检查Stripe环境变量
stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
stripe_public_key = os.environ.get('VITE_STRIPE_PUBLIC_KEY')

print(f"Stripe Secret Key: {'已设置' if stripe_secret_key else '未设置'}")
print(f"Stripe Public Key: {'已设置' if stripe_public_key else '未设置'}")

# 测试支付流程
def test_payment_flow():
    # 检查是否有用户
    if User.objects.count() == 0:
        print("创建测试用户...")
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpassword'
        )
    else:
        user = User.objects.first()
        print(f"使用现有用户: {user.username}")
    
    # 登录
    client.login(username=user.username, password='testpassword')
    
    # 检查是否有车辆数据
    if Car.objects.count() == 0:
        print("没有可用的车辆数据，请先运行setup_data.py")
        return
    
    car = Car.objects.first()
    print(f"测试车辆: {car.make} {car.model}")
    
    # 检查是否有地点数据
    if Location.objects.count() == 0:
        print("没有可用的地点数据，请先运行setup_data.py")
        return
    
    location = Location.objects.first()
    print(f"测试地点: {location.name}")
    
    # 1. 创建预订
    print("\n1. 创建预订...")
    # 注意：在实际应用中，这应该通过表单提交完成
    # 这里我们模拟POST请求
    response = client.post(reverse('create_booking', args=[car.id]), {
        'pickup_location': location.id,
        'dropoff_location': location.id,
        'pickup_date': '2025-04-15',
        'return_date': '2025-04-20',
        'driver_age': 25
    })
    
    if response.status_code == 302:  # 重定向是成功的标志
        print("预订创建成功！重定向到选项页面")
        # 从重定向URL提取临时预订ID
        redirect_url = response.url
        temp_booking_id = redirect_url.split('/')[-2]
        print(f"临时预订ID: {temp_booking_id}")
        
        # 2. 添加选项
        print("\n2. 添加选项...")
        response = client.post(reverse('confirm_booking', args=[temp_booking_id]), {
            'damage_waiver': 'on',
            'extended_area': 'on',
            'satellite_navigation': 'on',
            'child_seats': 1,
            'additional_drivers': 1
        })
        
        if response.status_code == 302:
            print("选项添加成功！重定向到支付页面")
            
            # 3. 模拟支付过程
            print("\n3. 处理支付...")
            response = client.post(reverse('process_payment', args=[temp_booking_id]), {
                'action': 'confirm'
            })
            
            if response.status_code == 302:
                redirect_url = response.url
                booking_id = redirect_url.split('/')[-2]
                print(f"支付成功！重定向到成功页面，预订ID: {booking_id}")
                
                # 4. 查看预订详情
                booking = Booking.objects.get(id=booking_id)
                print("\n4. 预订详情:")
                print(f"用户: {booking.user.username}")
                print(f"车辆: {booking.car.make} {booking.car.model}")
                print(f"取车地点: {booking.pickup_location.name}")
                print(f"还车地点: {booking.dropoff_location.name}")
                print(f"取车日期: {booking.pickup_date}")
                print(f"还车日期: {booking.return_date}")
                print(f"状态: {booking.status}")
                print(f"总费用: ${booking.total_cost}")
                print(f"附加选项: 损坏豁免({booking.damage_waiver}), 扩展区域({booking.extended_area}), 卫星导航({booking.satellite_navigation})")
                print(f"儿童座椅: {booking.child_seats}, 附加驾驶员: {booking.additional_drivers}")
                
                return booking
            else:
                print(f"支付失败: {response.status_code}")
                return None
        else:
            print(f"添加选项失败: {response.status_code}")
            return None
    else:
        print(f"创建预订失败: {response.status_code}")
        return None

# 测试Stripe托管结账页面
def test_stripe_checkout():
    # 检查是否有用户
    if User.objects.count() == 0:
        print("创建测试用户...")
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpassword'
        )
    else:
        user = User.objects.first()
        print(f"使用现有用户: {user.username}")
    
    # 登录
    client.login(username=user.username, password='testpassword')
    
    # 获取车辆和地点
    car = Car.objects.first()
    location = Location.objects.first()
    
    # 1. 创建预订
    print("\n1. 创建预订...")
    response = client.post(reverse('create_booking', args=[car.id]), {
        'pickup_location': location.id,
        'dropoff_location': location.id,
        'pickup_date': '2025-05-15',
        'return_date': '2025-05-20',
        'driver_age': 30
    })
    
    # 从重定向URL提取临时预订ID
    redirect_url = response.url
    temp_booking_id = redirect_url.split('/')[-2]
    
    # 2. 添加选项
    print("\n2. 添加选项...")
    response = client.post(reverse('confirm_booking', args=[temp_booking_id]), {
        'damage_waiver': 'on',
        'extended_area': 'on',
        'satellite_navigation': 'on',
    })
    
    # 3. 访问支付页面（这应该会重定向到Stripe结账页面）
    print("\n3. 访问支付页面...")
    response = client.get(reverse('payment', args=[temp_booking_id]))
    
    if response.status_code == 302:
        redirect_url = response.url
        print(f"重定向到Stripe结账页面: {redirect_url}")
        
        # 4. 模拟从Stripe返回
        print("\n4. 模拟从Stripe结账页面返回...")
        response = client.get(reverse('stripe_success', args=[temp_booking_id]))
        
        if response.status_code == 302:
            redirect_url = response.url
            booking_id = redirect_url.split('/')[-2]
            print(f"成功处理Stripe回调！重定向到成功页面，预订ID: {booking_id}")
            
            # 查看预订详情
            booking = Booking.objects.get(id=booking_id)
            return booking
        else:
            print(f"处理Stripe回调失败: {response.status_code}")
            return None
    else:
        print(f"支付页面未重定向到Stripe: {response.status_code}")
        content = response.content.decode('utf-8')
        print(f"内容: {content[:200]}...") # 仅打印前200个字符
        return None

if __name__ == '__main__':
    # 运行标准支付流程测试
    print("\n===== 测试标准支付流程 =====")
    booking1 = test_payment_flow()
    
    # 运行Stripe托管结账测试
    print("\n===== 测试Stripe托管结账 =====")
    booking2 = test_stripe_checkout()
    
    print("\n===== 测试完成 =====")
    if booking1 and booking2:
        print("所有测试通过！支付集成功能正常工作。")
    else:
        print("部分测试失败，请检查日志和错误信息。")