from django.shortcuts import render, get_object_or_404
from cars.models import Car, CarCategory, VehicleCategory, VehicleCategoryType
from locations.models import Location, CityHighlight
from .models import Testimonial, CarSubscription
from cars.models import VehicleFuel
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rush_car_rental.settings')

def home(request):
    # 首先尝试使用新的车辆模型
    featured_vehicles = VehicleCategory.objects.filter(
        renting_category=True,
        category_type__web_available=True
    ).order_by('?')[:6]
    
    # 如果新模型没有足够数据，再使用旧模型补充
    if featured_vehicles.count() < 4:
        featured_cars = Car.objects.filter(is_available=True).order_by('?')[:6]
    else:
        featured_cars = []
    
    locations = Location.objects.all()
    
    # 同时提供旧和新的类别
    categories = CarCategory.objects.all()
    category_types = VehicleCategoryType.objects.filter(web_available=True)
    
    city_highlights = CityHighlight.objects.all()[:3]
    testimonials = Testimonial.objects.filter(is_active=True).order_by('?')[:3]
    
    context = {
        'featured_vehicles': featured_vehicles,
        'featured_cars': featured_cars,
        'locations': locations,
        'categories': categories,
        'category_types': category_types,
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
    
    # 获取所有位置
    locations = Location.objects.all()
    
    # 获取所有车辆类别
    car_categories = VehicleCategory.objects.values_list('vehicle_category', flat=True).distinct()
    
    # 获取所有燃料类型
    fuel_types = VehicleFuel.objects.all()
    
    # 获取所有座位数
    seat_numbers = VehicleCategory.objects.values_list('num_adults', flat=True).distinct()
    
    # 获取筛选参数
    selected_location = request.GET.get('pickup_location', '')
    selected_fuel_type = request.GET.get('fuel_type', '')
    selected_car_category = request.GET.get('car_category', '')
    selected_seat_number = request.GET.get('seat_number', '')
    
    # 应用筛选
    if selected_location:
        subscriptions = subscriptions.filter(location__name=selected_location)
    if selected_fuel_type:
        subscriptions = subscriptions.filter(fuel_type=selected_fuel_type)
    if selected_car_category:
        subscriptions = subscriptions.filter(vehicle_category__vehicle_category=selected_car_category)
    if selected_seat_number:
        subscriptions = subscriptions.filter(vehicle_category__num_adults=selected_seat_number)
    
    context = {
        'subscriptions': subscriptions,
        'locations': locations,
        'car_categories': car_categories,
        'fuel_types': fuel_types,
        'seat_numbers': seat_numbers,
        'selected_location': selected_location,
        'selected_fuel_type': selected_fuel_type,
        'selected_car_category': selected_car_category,
        'selected_seat_number': selected_seat_number,
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
