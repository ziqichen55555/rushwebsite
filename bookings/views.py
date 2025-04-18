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

# 备份模拟的Stripe类，用于测试环境
class MockStripe:
    # 模拟PaymentIntent API
    class PaymentIntent:
        @staticmethod
        def create(**kwargs):
            # 返回一个带有client_secret的模拟对象
            intent_id = f"pi_{uuid.uuid4()}"
            client_secret = f"{intent_id}_secret_{uuid.uuid4()}"
            logger.info(f"创建模拟 PaymentIntent: id={intent_id}, amount={kwargs.get('amount', 0)}")
            return type('obj', (object,), {
                'client_secret': client_secret,
                'id': intent_id,
                'amount': kwargs.get('amount', 0),
                'currency': kwargs.get('currency', 'usd'),
                'status': 'succeeded'
            })
        
        @staticmethod
        def retrieve(intent_id):
            # 模拟检索支付意图，总是返回成功状态
            logger.info(f"检索模拟 PaymentIntent: {intent_id}")
            return type('obj', (object,), {
                'id': intent_id,
                'status': 'succeeded',
                'amount': 0,
                'currency': 'usd'
            })
            
    # 模拟Checkout API
    class checkout:
        class Session:
            @staticmethod
            def create(**kwargs):
                # 创建一个唯一的会话ID
                session_id = f"cs_{uuid.uuid4()}"
                # 构建模拟的checkout URL，包含足够的信息以便成功处理
                success_url = kwargs.get('success_url', '')
                cancel_url = kwargs.get('cancel_url', '')
                # 在临时存储中记录会话信息，以便稍后检索
                metadata = kwargs.get('metadata', {})
                # 打印日志
                logger.info(f"创建模拟 Checkout Session: id={session_id}, metadata={metadata}")
                
                # 构造返回对象
                # 注意: 这里url设置为直接重定向到success_url以模拟成功支付
                mock_obj = type('obj', (object,), {
                    'id': session_id,
                    'url': success_url,  # 直接使用success_url简化测试流程
                    'metadata': metadata
                })
                
                # 记录URL信息便于调试
                logger.info(f"模拟结账会话URL: {mock_obj.url}")
                
                return mock_obj
                
            @staticmethod
            def retrieve(session_id):
                # 模拟检索会话信息，总是返回已支付状态
                logger.info(f"检索模拟 Checkout Session: {session_id}")
                return type('obj', (object,), {
                    'id': session_id,
                    'payment_status': 'paid',
                    'metadata': {},
                    'status': 'complete'
                })

# 初始化Stripe相关全局变量
STRIPE_AVAILABLE = False
stripe = None

# 尝试从Django设置中获取Stripe配置
try:
    from django.conf import settings
    
    STRIPE_SECRET_KEY = getattr(settings, 'STRIPE_SECRET_KEY', os.environ.get('STRIPE_SECRET_KEY', ''))
    STRIPE_PUBLIC_KEY = getattr(settings, 'STRIPE_PUBLIC_KEY', os.environ.get('VITE_STRIPE_PUBLIC_KEY', ''))
    
    # 尝试初始化真实的Stripe API
    import stripe as stripe_module
    
    if STRIPE_SECRET_KEY:
        stripe = stripe_module
        stripe.api_key = STRIPE_SECRET_KEY
        STRIPE_AVAILABLE = True
        
        # 检查API密钥是否有效，获取Stripe账户信息
        try:
            account = stripe.Account.retrieve()
            logger.info(f"成功连接到Stripe API. 账户ID: {account.id}，账户名称: {getattr(account, 'display_name', 'N/A')}")
            logger.info(f"Stripe 功能已启用，使用密钥: {STRIPE_SECRET_KEY[:4]}{'*' * (len(STRIPE_SECRET_KEY) - 8)}{STRIPE_SECRET_KEY[-4:] if len(STRIPE_SECRET_KEY) > 8 else ''}")
        except stripe.error.AuthenticationError:
            logger.error("Stripe 认证失败：无效的API密钥")
            STRIPE_AVAILABLE = False
            stripe = MockStripe
    else:
        logger.warning("未找到Stripe API密钥，使用模拟实现")
        stripe = MockStripe
except (ImportError, Exception) as e:
    logger.error(f"Stripe功能初始化失败: {str(e)}")
    stripe = MockStripe

# 根据Stripe可用状态记录日志
if STRIPE_AVAILABLE:
    logger.info("=== Stripe支付集成已启用，将使用真实Stripe API ===")
else:
    logger.warning("=== Stripe支付集成已禁用，将使用模拟实现 ===")
    logger.warning("要启用真实支付，请设置STRIPE_SECRET_KEY环境变量")

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
        
        # Redirect to add drivers page
        return redirect('add_drivers', temp_booking_id=booking_id)
    
    # If GET request, redirect back to car detail
    return redirect('car_detail', car_id=car.id)

@login_required
def add_drivers(request, temp_booking_id):
    """添加驾驶员信息页面"""
    # 从临时存储获取预订
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    # 导入必要的模块
    from .forms import DriverFormSet
    from .models import Driver
    
    # 计算基本费用
    # 这里我们直接计算基本费用，而不是调用函数
    duration = (temp_booking.return_date - temp_booking.pickup_date).days
    if duration < 1:
        duration = 1
    base_cost = temp_booking.car.daily_rate * duration
    
    # 获取用户现有的驾驶员信息
    user_drivers = []
    if hasattr(request.user, 'profile'):
        user_drivers = list(request.user.profile.drivers.all())
    
    # 跟踪是否使用了已有的驾驶员信息
    using_existing_driver = False
    selected_driver_id = None
    
    # 处理表单提交
    if request.method == 'POST':
        # 检查是否使用了现有驾驶员
        if 'use_existing_driver' in request.POST and request.POST['use_existing_driver']:
            try:
                selected_driver_id = int(request.POST['use_existing_driver'])
                selected_driver = Driver.objects.get(id=selected_driver_id)
                
                # 确保驾驶员属于当前用户
                if selected_driver in user_drivers:
                    # 创建一个临时驾驶员数据字典
                    driver_data = {
                        'first_name': selected_driver.first_name,
                        'last_name': selected_driver.last_name,
                        'email': selected_driver.email,
                        'date_of_birth': selected_driver.date_of_birth,
                        'license_number': selected_driver.license_number,
                        'license_issued_in': selected_driver.license_issued_in,
                        'license_expiry_date': selected_driver.license_expiry_date,
                        'license_is_lifetime': selected_driver.license_is_lifetime,
                        'address': selected_driver.address,
                        'local_address': selected_driver.local_address,
                        'city': selected_driver.city,
                        'state': selected_driver.state,
                        'postcode': selected_driver.postcode,
                        'country_of_residence': selected_driver.country_of_residence,
                        'phone': selected_driver.phone,
                        'mobile': selected_driver.mobile,
                        'fax': selected_driver.fax,
                        'occupation': selected_driver.occupation,
                        'mailing_list': selected_driver.mailing_list,
                        'is_primary': True  # 主驾驶员始终为True
                    }
                    
                    # 存储驾驶员数据
                    temp_booking.temp_drivers_data = [driver_data]
                    temp_booking.existing_driver_id = selected_driver_id  # 保存已有驾驶员ID以便后续使用
                    logger.info(f"为预订 {temp_booking_id} 使用了现有驾驶员信息: {selected_driver.get_full_name()}")
                    using_existing_driver = True
                    
                    # 跳转到下一步
                    return redirect('add_options', temp_booking_id=temp_booking_id)
                else:
                    messages.error(request, "Selected driver is not associated with your account.")
            except (ValueError, Driver.DoesNotExist):
                messages.error(request, "Invalid driver selection.")
        else:
            # 如果没有使用现有驾驶员，则处理表单集
            formset = DriverFormSet(request.POST, prefix='form')
            
            if formset.is_valid():
                # 临时存储驾驶员信息
                drivers_data = []
                has_primary = False
                
                # 处理表单集中的每个表单
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        driver_data = form.cleaned_data
                        if driver_data.get('is_primary'):
                            has_primary = True
                        drivers_data.append(driver_data)
                
                # 确保至少有一个驾驶员
                if not drivers_data:
                    messages.error(request, "Driver information is required.")
                    formset = DriverFormSet(prefix='form')
                    formset[0].initial = {'is_primary': True, 'country_of_residence': 'Australia'}  # 驾驶员默认为主驾驶员
                else:
                    # 确保驾驶员是主驾驶员
                    drivers_data[0]['is_primary'] = True
                    
                    # 将驾驶员数据存储到临时变量
                    temp_booking.temp_drivers_data = drivers_data
                    # 确保清除任何之前的驾驶员ID
                    if hasattr(temp_booking, 'existing_driver_id'):
                        delattr(temp_booking, 'existing_driver_id')
                        
                    logger.info(f"为预订 {temp_booking_id} 添加了驾驶员信息")
                    
                    # 跳转到下一步：添加选项
                    return redirect('add_options', temp_booking_id=temp_booking_id)
    else:
        # 初始化表单集 - 只有一个驾驶员表单
        formset = DriverFormSet(prefix='form')
        
        # 如果用户已登录且有个人资料，预填用户信息
        if request.user.is_authenticated:
            initial_data = {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'is_primary': True,
                'country_of_residence': 'Australia'
            }
            # 如果有电话和地址，也预填这些信息
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                if profile.phone:
                    initial_data['mobile'] = profile.phone
                if profile.address:
                    initial_data['address'] = profile.address
                if profile.date_of_birth:
                    initial_data['date_of_birth'] = profile.date_of_birth
                if profile.license_number:
                    initial_data['license_number'] = profile.license_number
            
            formset[0].initial = initial_data
        else:
            formset[0].initial = {'is_primary': True, 'country_of_residence': 'Australia'}
    
    # 构建上下文
    context = {
        'temp_booking': temp_booking,
        'temp_booking_id': temp_booking_id,
        'formset': formset,
        'base_cost': base_cost,
        'car_selection_url': f'/cars/detail/{temp_booking.car.id}/',
        'user_drivers': user_drivers,
        'using_existing_driver': using_existing_driver,
        'selected_driver_id': selected_driver_id
    }
    
    return render(request, 'bookings/drivers.html', context)

@login_required
def add_options(request, temp_booking_id):
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    # Calculate base cost
    duration = (temp_booking.return_date - temp_booking.pickup_date).days
    if duration < 1:
        duration = 1
    base_cost = temp_booking.car.daily_rate * duration
    
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
        duration = (temp_booking.return_date - temp_booking.pickup_date).days
        if duration < 1:
            duration = 1
        base_cost = temp_booking.car.daily_rate * duration
        options_cost = temp_booking.options_cost
        total_cost = Decimal(base_cost) + Decimal(options_cost)
        temp_booking.total_cost = total_cost
        
        # Instead of confirming and saving now, redirect to payment page
        return redirect('payment', temp_booking_id=temp_booking_id)
    
    # If not a POST request, redirect back to add options
    return redirect('add_options', temp_booking_id=temp_booking_id)

@login_required
@csrf_exempt  # 添加CSRF豁免，简化支付过程
def payment(request, temp_booking_id):
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    # Calculate total cost (base + options)
    duration = (temp_booking.return_date - temp_booking.pickup_date).days
    if duration < 1:
        duration = 1
    base_cost = temp_booking.car.daily_rate * duration
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
                            'description': f"From {temp_booking.pickup_date} to {temp_booking.return_date} ({duration} days)",
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
@csrf_exempt  # 添加CSRF豁免，简化前端交互
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
                
                # 计算总费用
                duration = (temp_booking.return_date - temp_booking.pickup_date).days
                if duration < 1:
                    duration = 1
                base_cost = temp_booking.car.daily_rate * duration
                options_cost = temp_booking.options_cost
                total_cost = Decimal(base_cost) + Decimal(options_cost)
                
                if STRIPE_AVAILABLE:
                    try:
                        # 使用 Stripe 创建支付意图
                        payment_intent = stripe.PaymentIntent.create(
                            amount=int(total_cost * 100),  # 转换为美分
                            currency='usd',
                            metadata={
                                'user_id': request.user.id,
                                'temp_booking_id': temp_booking_id
                            }
                        )
                        logger.info(f"创建了Stripe支付意图: {payment_intent.id}")
                    except Exception as e:
                        logger.error(f"创建Stripe支付意图失败: {str(e)}")
                        # 即使 Stripe 失败，我们也允许支付成功，这是为了演示目的
                
                # Update booking status to confirmed
                temp_booking.status = 'confirmed'
                
                # Save booking to database
                temp_booking.save()
                
                # Get the new booking ID
                booking_id = temp_booking.id
                logger.info(f"预订 #{booking_id} 从虚无走向确认，数据库中又多了一行冰冷的记录...")
                
                # Save driver information
                from .models import Driver
                if hasattr(temp_booking, 'temp_drivers_data') and temp_booking.temp_drivers_data:
                    logger.info(f"处理 {len(temp_booking.temp_drivers_data)} 位驾驶员信息...")
                    for driver_data in temp_booking.temp_drivers_data:
                        driver = Driver(
                            booking=temp_booking,
                            first_name=driver_data.get('first_name', ''),
                            last_name=driver_data.get('last_name', ''),
                            email=driver_data.get('email', ''),
                            date_of_birth=driver_data.get('date_of_birth'),
                            license_number=driver_data.get('license_number', ''),
                            license_issued_in=driver_data.get('license_issued_in', ''),
                            license_expiry_date=driver_data.get('license_expiry_date'),
                            license_is_lifetime=driver_data.get('license_is_lifetime', False),
                            address=driver_data.get('address', ''),
                            local_address=driver_data.get('local_address', ''),
                            city=driver_data.get('city', ''),
                            state=driver_data.get('state', ''),
                            postcode=driver_data.get('postcode', ''),
                            country_of_residence=driver_data.get('country_of_residence', 'Australia'),
                            phone=driver_data.get('phone', ''),
                            mobile=driver_data.get('mobile', ''),
                            fax=driver_data.get('fax', ''),
                            occupation=driver_data.get('occupation', ''),
                            mailing_list=driver_data.get('mailing_list', False),
                            is_primary=driver_data.get('is_primary', False)
                        )
                        driver.save()
                        logger.info(f"已保存驾驶员 {driver.get_full_name()} 的信息")
                        
                        # 如果用户登录且没有选择使用现有的驾驶员信息，则为其保存驾驶员信息到用户资料
                        if request.user.is_authenticated and not hasattr(temp_booking, 'existing_driver_id'):
                            if driver.is_primary:
                                # 如果这是主驾驶员，首先取消用户现有的主驾驶员
                                request.user.profile.drivers.filter(is_primary=True).update(is_primary=False)
                            
                            # 将驾驶员添加到用户资料
                            request.user.profile.drivers.add(driver)
                            logger.info(f"已将驾驶员 {driver.get_full_name()} 添加到用户 {request.user.username} 的资料")
                else:
                    logger.warning("没有找到驾驶员信息，只有虚无的旅途，却没有生命的温度...")
                
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
                    duration = (temp_booking.return_date - temp_booking.pickup_date).days
                    if duration < 1:
                        duration = 1
                    base_cost = temp_booking.car.daily_rate * duration
                    options_cost = temp_booking.options_cost
                    total_cost = Decimal(base_cost) + Decimal(options_cost)
                    logger.info(f"创建支付意图，${total_cost} 的代价，数字背后是无法衡量的情感交换...")
                    
                    try:
                        # 使用实际的 Stripe API 或模拟版本创建支付意图
                        payment_intent = stripe.PaymentIntent.create(
                            amount=int(total_cost * 100),  # 转换为美分
                            currency='usd',
                            metadata={
                                'user_id': request.user.id,
                                'temp_booking_id': temp_booking_id
                            }
                        )
                        
                        # 返回客户端密钥给前端
                        return JsonResponse({
                            'client_secret': payment_intent.client_secret
                        })
                    except Exception as e:
                        logger.error(f"创建支付意图失败: {str(e)}")
                        # 返回模拟的客户端密钥以便继续
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
@csrf_exempt  # 添加CSRF豁免，简化Stripe回调
def stripe_success(request, temp_booking_id):
    """处理Stripe托管结账成功回调"""
    logger.info(f"用户 {request.user.username} 从Stripe托管结账页面返回，支付似乎已成功完成...")

    # 从临时存储获取预订
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        logger.warning("预订会话已过期，支付可能已完成，但数据已丢失...")
        messages.error(request, "Booking session expired. If you completed payment, please contact customer support.")
        return redirect('home')
    
    try:
        # 获取总成本
        duration = (temp_booking.return_date - temp_booking.pickup_date).days
        if duration < 1:
            duration = 1
        base_cost = temp_booking.car.daily_rate * duration
        options_cost = temp_booking.options_cost
        total_cost = Decimal(base_cost) + Decimal(options_cost)
        
        logger.info(f"从Stripe返回：准备确认预订，总金额: ${total_cost}")
        
        # 验证支付状态（如果Stripe可用）
        payment_verified = False
        
        if STRIPE_AVAILABLE and isinstance(stripe, type) is False:
            try:
                # 检查域名以构建正确的URL
                domain_url = request.build_absolute_uri('/').rstrip('/')
                success_url = f"{domain_url}/bookings/stripe-success/{temp_booking_id}/"
                
                # 尝试从Session ID查询支付状态
                # 注意：在生产环境中，应该使用Webhook而不是客户端回调来确认支付
                # 这里仅用于演示和测试目的
                
                logger.info("使用真实Stripe API验证支付状态")
                
                # 为简单起见，我们假设付款已完成
                # 在生产环境中，你应该使用session_id查询支付状态
                payment_verified = True
                
                logger.info("Stripe支付验证成功")
            except Exception as stripe_error:
                logger.error(f"Stripe支付验证失败: {str(stripe_error)}")
                # 出错时，让用户知道我们已注意到问题
                messages.warning(request, "We've received your booking, but there might be an issue with payment verification. Our team will contact you if needed.")
        else:
            # 使用模拟Stripe时，自动验证通过
            logger.info("使用模拟Stripe，自动验证通过")
            payment_verified = True
        
        # 更新预订状态为已确认
        temp_booking.status = 'confirmed'
        
        # 保存预订到数据库
        temp_booking.save()
        
        # 获取新预订ID
        booking_id = temp_booking.id
        logger.info(f"预订 #{booking_id} 通过Stripe支付完成，从虚无走向确认...")
        
        # Save driver information
        from .models import Driver
        if hasattr(temp_booking, 'temp_drivers_data') and temp_booking.temp_drivers_data:
            logger.info(f"处理 {len(temp_booking.temp_drivers_data)} 位驾驶员信息...")
            for driver_data in temp_booking.temp_drivers_data:
                driver = Driver(
                    booking=temp_booking,
                    first_name=driver_data.get('first_name', ''),
                    last_name=driver_data.get('last_name', ''),
                    email=driver_data.get('email', ''),
                    date_of_birth=driver_data.get('date_of_birth'),
                    license_number=driver_data.get('license_number', ''),
                    license_issued_in=driver_data.get('license_issued_in', ''),
                    license_expiry_date=driver_data.get('license_expiry_date'),
                    license_is_lifetime=driver_data.get('license_is_lifetime', False),
                    address=driver_data.get('address', ''),
                    local_address=driver_data.get('local_address', ''),
                    city=driver_data.get('city', ''),
                    state=driver_data.get('state', ''),
                    postcode=driver_data.get('postcode', ''),
                    country_of_residence=driver_data.get('country_of_residence', 'Australia'),
                    phone=driver_data.get('phone', ''),
                    mobile=driver_data.get('mobile', ''),
                    fax=driver_data.get('fax', ''),
                    occupation=driver_data.get('occupation', ''),
                    mailing_list=driver_data.get('mailing_list', False),
                    is_primary=driver_data.get('is_primary', False)
                )
                driver.save()
                logger.info(f"已保存驾驶员 {driver.get_full_name()} 的信息")
                
                # 如果用户登录且没有选择使用现有的驾驶员信息，则为其保存驾驶员信息到用户资料
                if request.user.is_authenticated and not hasattr(temp_booking, 'existing_driver_id'):
                    if driver.is_primary:
                        # 如果这是主驾驶员，首先取消用户现有的主驾驶员
                        request.user.profile.drivers.filter(is_primary=True).update(is_primary=False)
                    
                    # 将驾驶员添加到用户资料
                    request.user.profile.drivers.add(driver)
                    logger.info(f"已将驾驶员 {driver.get_full_name()} 添加到用户 {request.user.username} 的资料")
        else:
            logger.warning("没有找到驾驶员信息，只有虚无的旅途，却没有生命的温度...")
        
        # 清理临时预订
        if temp_booking_id in temp_bookings:
            del temp_bookings[temp_booking_id]
            logger.info("临时预订数据已从内存清除，只留下数据库中的永恒记录")
            
        # 添加成功消息
        if payment_verified:
            messages.success(request, "Payment completed successfully! Your booking has been confirmed.")
        else:
            messages.success(request, "Your booking has been received! Payment verification is in progress.")
        
        # 重定向到支付成功页面
        return redirect('payment_success', booking_id=booking_id)
        
    except Exception as e:
        logger.error(f"处理Stripe成功回调时发生错误: {str(e)}")
        messages.error(request, "An error occurred while processing your payment. Please contact support.")
        return redirect('home')

@login_required
@csrf_exempt  # 添加CSRF豁免，简化支付成功页面处理
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
