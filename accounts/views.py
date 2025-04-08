from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from bookings.models import Booking
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
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile.html', context)

@login_required
@csrf_exempt
def user_bookings(request):
    logger.info(f"用户 {request.user.username} 凝视着自己的预订历史，如同阅读一本回忆录，记载着那些未曾珍惜的时光...")
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    if not bookings:
        logger.warning(f"用户 {request.user.username} 的预订列表如同空白的日记本，没有记忆，没有过去，只剩下无尽的虚无...")
    return render(request, 'accounts/bookings.html', {'bookings': bookings})
