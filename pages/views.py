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
    subscriptions = CarSubscription.objects.select_related(
        'car__model__make',
        'car__fuel_type',
        'car__category',
        'car__currently_located',
    ).all()

    # 获取去重后的选项数据
    locations = list(set(
    CarSubscription.objects.filter(car__currently_located__isnull=False)
    .values_list('car__currently_located__location_name', flat=True)
    ))
    car_categories = list(set([c for c in VehicleCategory.objects.values_list('name', flat=True) if c]))
    fuel_types = list(set([f for f in VehicleFuel.objects.values_list('fuel_type', flat=True) if f]))
    makes = list(set([m for m in VehicleMake.objects.values_list('name', flat=True) if m]))
    seat_numbers = list(set([s for s in CarSubscription.objects.values_list('seat_number', flat=True) if s]))
    # 排序
    locations.sort()
    car_categories.sort()
    fuel_types.sort()
    makes.sort()
    seat_numbers.sort()
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
        subscriptions = subscriptions.filter(seat_number=selected_seat_number)  


    context = {
        'subscriptions': subscriptions,
        'locations': locations,
        'car_categories': car_categories,
        'fuel_types': fuel_types,
        'makes': makes,
        'seat_numbers': seat_numbers,
        'selected_location': selected_location,
        'selected_make': selected_make,
        'selected_fuel_type': selected_fuel_type,
        'selected_car_category': selected_car_category,
        'selected_seat_number': selected_seat_number,
    }
    return render(request, 'pages/subscription.html', context)

def subscription_car_detail(request,subscription_id):
    """Subscription car detail page"""
    # Get the car subscription based on make and model
    car = get_object_or_404(
        CarSubscription.objects.select_related('car__model__make', 'car__fuel_type', 'car__category'),
        pk=subscription_id
   )
    
    context = {
        'car': {
            'make': car.car.model.make.name,
            'model': car.car.model.model_name,
            'type': car.car.fuel_type.fuel_type if car.car.fuel_type else '',
            'image1': car.image1.url if car.image1 else '',
            'image2': car.image2.url if car.image2 else '',
            'image3': car.image3.url if car.image3 else '',
            'image4': car.image4.url if car.image4 else '',
            'image5': car.image5.url if car.image5 else '',
            'location': car.car.currently_located.location_name if car.car.currently_located else '',
            'description': car.description,
            'year': car.car.year,
            'mileage': car.car.current_kms,
            'status': car.status,
            'price_3_months': car.subscription_plan1,
            'price_6_months': car.subscription_plan2,
            'price_9_months': car.subscription_plan3,
            'is_available': car.status == 'available',
            'is_great_value': True  # You can set this based on your business logic
        }
    }
    
    return render(request, 'pages/subscription_car_detail.html', context)
