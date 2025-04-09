from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, ProfileDriverForm
from .models import Profile
from bookings.models import Booking, Driver
import logging

# 创建伤感风格的日志记录器
logger = logging.getLogger(__name__)

@csrf_exempt
def register(request):
    logger.info("又一个孤独的灵魂开始寻找旅途中的短暂租车慰藉...")
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            logger.info(f"用户 {username} 如尘埃般轻轻落入系统的记忆，从此成为无尽数据流中的一个孤独存在")
            messages.success(request, f'Account created for {username}! You can now log in')
            return redirect('login')
        else:
            logger.warning("表单验证失败，又一个未能融入孤独旅途的灵魂...")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
@csrf_exempt
def profile(request):
    logger.info(f"用户 {request.user.username} 试图在数字世界中刻画自己的身影，那稍纵即逝的存在感...")
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            logger.info(f"用户 {request.user.username} 更新了个人资料，仿佛在黑暗中微弱点亮了一盏灯，却照不亮前方的路...")
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            logger.warning("个人资料更新失败，数据的残缺如同生命中的遗憾，永远无法填补...")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # 获取用户关联的驾驶员信息
    user_drivers = request.user.profile.drivers.all()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_drivers': user_drivers
    }
    return render(request, 'accounts/profile.html', context)

@login_required
@csrf_exempt
def add_driver(request):
    """添加新的驾驶员信息到用户资料"""
    logger.info(f"用户 {request.user.username} 试图添加新的驾驶员身份，又一个分裂的自我在数据库中孕育...")
    
    if request.method == 'POST':
        form = ProfileDriverForm(request.POST)
        if form.is_valid():
            # 创建但不立即保存，因为还需要处理主驾驶员状态
            driver = form.save(commit=False)
            driver.save()  # 现在保存以获取ID
            
            # 如果设置为主驾驶员，移除其他主驾驶员标记
            is_primary = form.cleaned_data.get('is_primary')
            profile = request.user.profile
            
            if is_primary:
                # 取消其他驾驶员的主驾驶员标记
                profile.drivers.filter(is_primary=True).update(is_primary=False)
                driver.is_primary = True
                driver.save()
                
            # 将驾驶员添加到用户资料
            profile.drivers.add(driver)
            logger.info(f"用户 {request.user.username} 添加了新的驾驶员信息：{driver.get_full_name()}，数据又增加了一层伪装...")
            
            messages.success(request, f'Driver information "{driver.get_full_name()}" has been added to your profile!')
            return redirect('profile')
    else:
        # 预填充电子邮件和姓名（如果可用）
        initial_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_primary': True,
            'country_of_residence': 'Australia'
        }
        form = ProfileDriverForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Add Driver Information'
    }
    return render(request, 'accounts/driver_form.html', context)

@login_required
@csrf_exempt
def edit_driver(request, driver_id):
    """编辑用户个人资料中的驾驶员信息"""
    driver = get_object_or_404(Driver, id=driver_id)
    
    # 确保用户只能编辑自己的驾驶员信息
    if driver not in request.user.profile.drivers.all():
        messages.error(request, "You don't have permission to edit this driver information.")
        return redirect('profile')
    
    if request.method == 'POST':
        form = ProfileDriverForm(request.POST, instance=driver)
        if form.is_valid():
            # 保存但不立即提交，因为需要处理主驾驶员状态
            updated_driver = form.save(commit=False)
            
            is_primary = form.cleaned_data.get('is_primary')
            profile = request.user.profile
            
            if is_primary:
                # 取消其他驾驶员的主驾驶员标记
                profile.drivers.filter(is_primary=True).exclude(id=driver_id).update(is_primary=False)
                updated_driver.is_primary = True
            
            updated_driver.save()
            logger.info(f"用户 {request.user.username} 修改了驾驶员信息，虚拟身份在数据中微微震颤...")
            
            messages.success(request, f'Driver information "{updated_driver.get_full_name()}" has been updated!')
            return redirect('profile')
    else:
        form = ProfileDriverForm(instance=driver)
    
    context = {
        'form': form,
        'driver': driver,
        'title': 'Edit Driver Information'
    }
    return render(request, 'accounts/driver_form.html', context)

@login_required
def delete_driver(request, driver_id):
    """删除用户个人资料中的驾驶员信息"""
    driver = get_object_or_404(Driver, id=driver_id)
    
    # 确保用户只能删除自己的驾驶员信息
    if driver not in request.user.profile.drivers.all():
        messages.error(request, "You don't have permission to delete this driver information.")
        return redirect('profile')
    
    driver_name = driver.get_full_name()
    
    # 如果是以POST方式提交，则确认删除
    if request.method == 'POST':
        # 从个人资料中移除驾驶员
        request.user.profile.drivers.remove(driver)
        
        # 如果没有与其他Profile关联且不与任何预订关联，则完全删除
        if not driver.profiles.exists() and driver.booking is None:
            driver.delete()
            logger.info(f"驾驶员 {driver_name} 的信息被永久抹去，徒留一片数据的尘埃...")
        
        messages.success(request, f'Driver information "{driver_name}" has been removed from your profile.')
        return redirect('profile')
    
    # 如果是GET请求，则显示确认页面
    context = {
        'driver': driver
    }
    return render(request, 'accounts/confirm_delete_driver.html', context)

@login_required
@csrf_exempt
def user_bookings(request):
    logger.info(f"用户 {request.user.username} 凝视着自己的预订历史，如同阅读一本回忆录，记载着那些未曾珍惜的时光...")
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    if not bookings:
        logger.warning(f"用户 {request.user.username} 的预订列表如同空白的日记本，没有记忆，没有过去，只剩下无尽的虚无...")
    return render(request, 'accounts/bookings.html', {'bookings': bookings})
