from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from decimal import Decimal
import json
import os
import uuid
import logging
from .models import Booking
from cars.models import Car
from locations.models import Location

# 创建伤感风格的日志记录器
logger = logging.getLogger(__name__)

# 尝试导入Stripe，如果失败，使用模拟实现
try:
    import stripe
    # 设置Stripe API密钥
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_AVAILABLE = True
    print(f"Stripe 功能已启用，使用密钥: {os.environ.get('STRIPE_SECRET_KEY')[:5]}...")
except (ImportError, Exception) as e:
    print(f"Stripe功能不可用: {str(e)}")
    STRIPE_AVAILABLE = False
    
    # 创建一个模拟的Stripe类，只用于测试
    class MockStripe:
        class PaymentIntent:
            @staticmethod
            def create(**kwargs):
                # 返回一个带有client_secret的模拟对象
                return type('obj', (object,), {
                    'client_secret': f"mock_pi_secret_{uuid.uuid4()}_{kwargs.get('amount', 0)}",
                    'id': f"pi_{uuid.uuid4()}",
                    'amount': kwargs.get('amount', 0),
                    'currency': kwargs.get('currency', 'usd'),
                    'status': 'succeeded'
                })
                
        class Checkout:
            class Session:
                @staticmethod
                def create(**kwargs):
                    # 返回一个带有id和url的模拟对象
                    return type('obj', (object,), {
                        'id': f"cs_{uuid.uuid4()}",
                        'url': f"/mock-stripe-checkout/{uuid.uuid4()}",
                    })
    
    # 如果Stripe不可用，使用模拟实现
    if not STRIPE_AVAILABLE:
        stripe = MockStripe

# Dictionary to store temporary bookings
temp_bookings = {}

@login_required
def create_booking(request, car_id):
    logger.info(f"用户 {request.user.username} 开始寻找一辆车，遗忘在时光中的微小身影，像沙漠中的一粒尘土...")
    car = get_object_or_404(Car, pk=car_id)
    logger.info(f"选择了 {car.make} {car.model}，这辆车将承载着短暂的旅程，然后离他而去，就像生命中的所有过客...")
    
    if request.method == 'POST':
        pickup_location_id = request.POST.get('pickup_location')
        dropoff_location_id = request.POST.get('dropoff_location')
        pickup_date_str = request.POST.get('pickup_date')
        return_date_str = request.POST.get('return_date')
        driver_age = request.POST.get('driver_age')
        
        # Validate data
        errors = []
        
        if not pickup_location_id:
            errors.append("Pickup location is required")
        
        if not dropoff_location_id:
            errors.append("Drop-off location is required")
        
        try:
            pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
            if pickup_date < timezone.now().date():
                errors.append("Pickup date cannot be in the past")
                logger.warning("试图预订过去的时间，就像想要挽回那些已经逝去的记忆，徒劳而心碎...")
        except (ValueError, TypeError):
            errors.append("Invalid pickup date")
            pickup_date = None
            logger.warning("日期格式错误，时间总是如此难以把握，就像从指间流逝的细沙...")
        
        try:
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
            if pickup_date and return_date < pickup_date:
                errors.append("Return date must be after pickup date")
                logger.warning("归还日期早于取车日期，时间的逻辑被打破，就像破碎的镜子反射着扭曲的现实...")
        except (ValueError, TypeError):
            errors.append("Invalid return date")
            return_date = None
            logger.warning("无效的归还日期，未知的终点，像是迷失在无边黑暗中的旅人...")
        
        try:
            driver_age = int(driver_age)
            if driver_age < 18:
                errors.append("Driver must be at least 18 years old")
                logger.warning(f"驾驶员年龄 {driver_age} 不足，年少轻狂却无法触及远方，束缚是成长的代价...")
        except (ValueError, TypeError):
            errors.append("Invalid driver age")
            logger.warning("无效的驾驶员年龄，数字也有其局限性，无法量化人生的沧桑...")
        
        # If there are errors, show them to the user
        if errors:
            for error in errors:
                messages.error(request, error)
            logger.error(f"预订表单验证失败，希望破灭的声音在用户 {request.user.username} 心中回荡...")
            return redirect('car_detail', car_id=car.id)
        
        # Calculate total cost
        duration = (return_date - pickup_date).days
        if duration < 1:
            duration = 1
        total_cost = car.daily_rate * duration
        logger.info(f"行程 {duration} 天，总费用 ${total_cost}，金钱换取短暂的自由，多么悲哀的交易...")
        
        # Create a temporary booking object
        temp_booking = Booking(
            user=request.user,
            car=car,
            pickup_location=Location.objects.get(pk=pickup_location_id),
            dropoff_location=Location.objects.get(pk=dropoff_location_id),
            pickup_date=pickup_date,
            return_date=return_date,
            total_cost=total_cost,
            driver_age=driver_age,
            status='pending'  # Stay as pending until confirmed
        )
        
        # Store in temp_bookings dictionary with a unique ID
        import uuid
        booking_id = str(uuid.uuid4())
        temp_bookings[booking_id] = temp_booking
        logger.info(f"预订 {booking_id} 暂存于系统的记忆中，像一个漂泊的梦，等待着最终的命运...")
        
        # Redirect to add options page
        return redirect('add_options', temp_booking_id=booking_id)
    
    # If GET request, redirect back to car detail
    return redirect('car_detail', car_id=car.id)

@login_required
def add_options(request, temp_booking_id):
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    # Calculate base cost
    base_cost = temp_booking.car.daily_rate * temp_booking.duration_days
    
    # Define costs for each option
    context = {
        'temp_booking': temp_booking,
        'temp_booking_id': temp_booking_id,  # Pass the ID to template
        'base_cost': base_cost,
        'damage_waiver_cost': 14,  # $14 per day
        'extended_area_cost': 150,  # $150 flat fee
        'gps_cost': 5,  # $5 per day
        'child_seat_cost': 8,  # $8 per day per seat
        'additional_driver_cost': 5,  # $5 per day per driver
    }
    
    return render(request, 'bookings/add_options.html', context)

@login_required
def confirm_booking(request, temp_booking_id):
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    if request.method == 'POST':
        # Get option selections from form
        # Check for both 'true' (from JavaScript) and 'on' (from HTML checkbox)
        damage_waiver_val = request.POST.get('damage_waiver', 'false')
        damage_waiver = damage_waiver_val == 'true' or damage_waiver_val == 'on'
        
        extended_area_val = request.POST.get('extended_area', 'false')
        extended_area = extended_area_val == 'true' or extended_area_val == 'on'
        
        satellite_navigation_val = request.POST.get('satellite_navigation', 'false')
        satellite_navigation = satellite_navigation_val == 'true' or satellite_navigation_val == 'on'
        
        try:
            child_seats = int(request.POST.get('child_seats', 0))
        except ValueError:
            child_seats = 0
            
        try:
            additional_drivers = int(request.POST.get('additional_drivers', 0))
        except ValueError:
            additional_drivers = 0
            
        # Print for debugging
        print(f"Form data: damage_waiver={damage_waiver_val}, extended_area={extended_area_val}, sat_nav={satellite_navigation_val}")
        
        # Apply options to temporary booking
        temp_booking.damage_waiver = damage_waiver
        temp_booking.extended_area = extended_area
        temp_booking.satellite_navigation = satellite_navigation
        temp_booking.child_seats = child_seats
        temp_booking.additional_drivers = additional_drivers
        
        # Update total cost with options
        base_cost = temp_booking.car.daily_rate * temp_booking.duration_days
        options_cost = temp_booking.options_cost
        total_cost = Decimal(base_cost) + Decimal(options_cost)
        temp_booking.total_cost = total_cost
        
        # Instead of confirming and saving now, redirect to payment page
        return redirect('payment', temp_booking_id=temp_booking_id)
    
    # If not a POST request, redirect back to add options
    return redirect('add_options', temp_booking_id=temp_booking_id)

@login_required
def payment(request, temp_booking_id):
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    # Calculate total cost (base + options)
    base_cost = temp_booking.car.daily_rate * temp_booking.duration_days
    options_cost = temp_booking.options_cost
    total_cost = Decimal(base_cost) + Decimal(options_cost)
    
    # 优先使用Stripe托管结账页面
    if STRIPE_AVAILABLE and os.environ.get('STRIPE_SECRET_KEY'):
        try:
            # 创建Stripe Checkout会话
            logger.info(f"为用户 {request.user.username} 创建Stripe结账会话，总金额: ${total_cost}")
            
            # 获取域名
            domain_url = request.build_absolute_uri('/').rstrip('/')
            
            # 创建一个结账会话
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Car Rental: {temp_booking.car.make} {temp_booking.car.model}",
                            'description': f"From {temp_booking.pickup_date} to {temp_booking.return_date} ({temp_booking.duration_days} days)",
                            'images': [temp_booking.car.image_url],
                        },
                        'unit_amount': int(total_cost * 100),  # Stripe需要以分为单位
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{domain_url}/bookings/stripe-success/{temp_booking_id}/",
                cancel_url=f"{domain_url}/bookings/payment/{temp_booking_id}/",
                metadata={
                    'temp_booking_id': temp_booking_id,
                    'user_id': request.user.id,
                }
            )
            
            # 重定向到Stripe结账页面
            return redirect(checkout_session.url)
            
        except Exception as e:
            logger.error(f"创建Stripe会话失败: {str(e)}")
            # 如果Stripe API调用失败，回退到标准支付页面
            messages.warning(request, "Payment processing service is temporarily unavailable. Please use our standard checkout.")
    
    # 如果Stripe不可用，使用标准支付页面
    # 模拟的客户端密钥
    mock_client_secret = f"mock_pi_secret_{temp_booking_id}_{int(total_cost)}"
    
    context = {
        'temp_booking': temp_booking,
        'temp_booking_id': temp_booking_id,
        'total_cost': total_cost,
        'stripe_public_key': os.environ.get('VITE_STRIPE_PUBLIC_KEY', 'pk_test_mock'),
        'client_secret': mock_client_secret,
    }
    
    return render(request, 'bookings/payment.html', context)

@login_required
def process_payment(request, temp_booking_id):
    logger.info(f"用户 {request.user.username} 将心血化作金钱，试图换取片刻的流动自由...")
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        logger.warning("预订会话已过期，如同冰雪消融，所有痕迹化为虚无...")
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # For regular form submission (most likely case now)
            if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
                action = request.POST.get('action', 'confirm')
                logger.info("金钱的象征在数字世界中流动，虚拟的交易，真实的代价...")
                
                # Process the payment - this would interact with Stripe in production
                # But for now, we'll just confirm the booking directly
                
                # Update booking status to confirmed
                temp_booking.status = 'confirmed'
                
                # Save booking to database
                temp_booking.save()
                
                # Get the new booking ID
                booking_id = temp_booking.id
                logger.info(f"预订 #{booking_id} 从虚无走向确认，数据库中又多了一行冰冷的记录...")
                
                # Clean up temporary booking
                if temp_booking_id in temp_bookings:
                    del temp_bookings[temp_booking_id]
                    logger.info("临时记忆被抹去，仿佛从未存在，就像我们终将被时间遗忘...")
                
                # Redirect to success page
                messages.success(request, "Payment successful! Your booking has been confirmed.")
                return redirect('payment_success', booking_id=booking_id)
                
            # For AJAX requests (JSON)
            else:
                try:
                    data = json.loads(request.body)
                    action = data.get('action', None)
                except json.JSONDecodeError:
                    action = 'confirm'
                    logger.warning("解析失败的JSON请求，破碎的数据如同支离破碎的思绪...")
                
                # Request to create payment intent only
                if action == 'create_intent':
                    # Calculate total price
                    base_cost = temp_booking.car.daily_rate * temp_booking.duration_days
                    options_cost = temp_booking.options_cost
                    total_cost = Decimal(base_cost) + Decimal(options_cost)
                    logger.info(f"创建支付意图，${total_cost} 的代价，数字背后是无法衡量的情感交换...")
                    
                    # Create mock client secret
                    mock_client_secret = f"mock_pi_secret_{temp_booking_id}_{int(total_cost)}"
                    
                    return JsonResponse({
                        'client_secret': mock_client_secret
                    })
                
                # Default action - handle payment confirmation
                else:
                    # Update booking status to confirmed
                    temp_booking.status = 'confirmed'
                    logger.info("交易的一瞬，命运的转折，从此踏上不可回头的旅程...")
                    
                    # Save booking to database
                    temp_booking.save()
                    
                    # Get the new booking ID
                    booking_id = temp_booking.id
                    
                    # Clean up temporary booking
                    if temp_booking_id in temp_bookings:
                        del temp_bookings[temp_booking_id]
                    
                    # Return JSON response for AJAX requests
                    return JsonResponse({
                        'success': True,
                        'booking_id': booking_id,
                        'redirect_url': f'/bookings/payment-success/{booking_id}/'
                    })
                
        except Exception as e:
            logger.error(f"支付过程中的错误是命运的捉弄，系统拒绝接受灵魂的交易: {str(e)}") 
            print(f"Error processing payment: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': str(e)
                }, status=400)
            messages.error(request, f"Payment processing failed: {str(e)}")
            return redirect('payment', temp_booking_id=temp_booking_id)
    
    # For GET requests - simplified flow for testing
    # In a real application, GET requests should not process payments
    # This is only for demonstration purposes
    logger.info("测试环境中的GET请求，虚假的支付，如同生活中的假象，我们宁愿相信美好的谎言...")
    temp_booking.status = 'confirmed'
    temp_booking.save()
    booking_id = temp_booking.id
    
    if temp_booking_id in temp_bookings:
        del temp_bookings[temp_booking_id]
    
    messages.success(request, "Payment successful! Your booking has been confirmed.")
    return redirect('payment_success', booking_id=booking_id)

@login_required
def stripe_success(request, temp_booking_id):
    """处理Stripe托管结账成功回调"""
    logger.info(f"用户 {request.user.username} 从Stripe托管结账页面返回，支付似乎已成功完成...")

    # 从临时存储获取预订
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        logger.warning("预订会话已过期，支付可能已完成，但数据已丢失...")
        messages.error(request, "Booking session expired. If you completed payment, please contact customer support.")
        return redirect('home')
    
    # 更新预订状态为已确认
    temp_booking.status = 'confirmed'
    
    # 保存预订到数据库
    temp_booking.save()
    
    # 获取新预订ID
    booking_id = temp_booking.id
    logger.info(f"预订 #{booking_id} 通过Stripe支付完成，从虚无走向确认...")
    
    # 清理临时预订
    if temp_booking_id in temp_bookings:
        del temp_bookings[temp_booking_id]
    
    messages.success(request, "Payment successful! Your booking has been confirmed.")
    return redirect('payment_success', booking_id=booking_id)

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'bookings/payment_success.html', {'booking': booking})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'bookings/booking_success.html', {'booking': booking})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    logger.info(f"用户 {request.user.username} 站在取消预订的十字路口，犹豫不决中蕴含着对自由的向往和对承诺的迷茫...")
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        logger.info(f"预订 #{booking_id} 如同一场雨后的彩虹，转瞬即逝，只余下数据库中status='cancelled'的冰冷标记...")
        logger.info(f"用户 {request.user.username} 的旅程变成了一个未曾发生的故事，就像那些我们从未讲述的梦...")
        messages.success(request, "Your booking has been cancelled")
        return redirect('user_bookings')
    
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})
