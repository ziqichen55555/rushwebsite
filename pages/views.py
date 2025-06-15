from django.shortcuts import render, get_object_or_404
from cars.models import Car, CarCategory, VehicleCategory, VehicleCategoryType,VehicleMake,VehicleModel,VehicleFuel,VehicleType,VehicleImage
from pages.models import CarSubscription
from locations.models import Location, CityHighlight
from .models import Testimonial
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')

def home(request):
    
    
    city_highlights = CityHighlight.objects.all()[:3]
    testimonials = Testimonial.objects.filter(is_active=True).order_by('?')[:3]
    
    context = {
        'city_highlights': city_highlights,
        'testimonials': testimonials
    }
    return render(request, 'home.html', context)

def rental_conditions(request):
    return render(request, 'pages/rental_conditions.html')

def refund_policy(request):
    return render(request, 'pages/refund_policy.html')

def complaint(request):
    return render(request, 'pages/complaint.html')
    
def pickup_guidelines(request):
    return render(request, 'pages/pickup_guidelines.html')
    
def return_guidelines(request):
    return render(request, 'pages/return_guidelines.html')
    
def about_us(request):
    return render(request, 'pages/about_us.html')
    
def subscription(request):
    # 获取所有订阅车辆数据
    subscriptions = CarSubscription.objects.all()
    models = VehicleModel.objects.all()
    # 获取所有位置
    locations = Location.objects.all()
    # 获取所有车辆类别
    car_categories = VehicleCategory.objects.all()
    # 获取所有燃料类型
    fuel_types = VehicleFuel.objects.all()
    # 获取所有车辆品牌
    makes = VehicleMake.objects.all()
    # 获取所有座位数
    seat_numbers = CarSubscription.objects.values_list('seat_number', flat=True).distinct()
    # 获取筛选参数
    selected_location = request.GET.get('pickup_location', '')
    selected_make = request.GET.get('make', '')
    selected_fuel_type = request.GET.get('fuel_type', '')
    selected_car_category = request.GET.get('car_category', '')
    selected_seat_number = request.GET.get('seat_number', '')

    # 应用筛选
    if selected_location:
        subscriptions = subscriptions.filter(car__currently_located__name=selected_location)
    if selected_make:
        subscriptions = subscriptions.filter(car__model__make__name=selected_make)
    if selected_fuel_type:
        subscriptions = subscriptions.filter(car__fuel_type__fuel_type=selected_fuel_type)
    if selected_car_category:
        subscriptions = subscriptions.filter(car__category__name=selected_car_category)
    if selected_seat_number:
        subscriptions = subscriptions.filter(car__seats=selected_seat_number)

    context = {
        'subscriptions': subscriptions,
        'models': models,
        'locations': locations,
        'car_categories': car_categories,
        'fuel_types': fuel_types,
        'makes': makes,
        'seat_numbers': seat_numbers,
        'selected_location': selected_location,
        'selected_fuel_type': selected_fuel_type,
        'selected_car_category': selected_car_category,
        'selected_seat_number': selected_seat_number,
        'selected_make': selected_make,
    }
    return render(request, 'pages/subscription.html', context)

def subscription_car_detail(request, make, model):
    """Subscription car detail page"""
    # Get the car subscription based on make and model
    car = get_object_or_404(
        CarSubscription.objects.select_related('model__make', 'vehicle_category', 'fuel_type'),
        model__make__name__iexact=make,
        model__model_name__iexact=model
    )
    
    context = {
        'car': {
            'make': car.model.make.name,
            'model': car.model.model_name,
            'type': car.fuel_type.name,
            'image_url': car.image1.url if car.image1 else '',
            'location': car.location.name,
            'description': car.description,
            'year': car.year,
            'mileage': car.mileage,
            'status': car.status,
            'price_3_months': car.subscription_plan1,
            'price_6_months': car.subscription_plan2,
            'price_9_months': car.subscription_plan3,
            'is_available': car.status == 'available',
            'is_great_value': True  # You can set this based on your business logic
        }
    }
    
    return render(request, 'pages/subscription_car_detail.html', context)
