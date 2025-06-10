from django.shortcuts import render
from cars.models import Car, CarCategory, VehicleCategory, VehicleCategoryType, VehicleType
from locations.models import Location, CityHighlight
from .models import Testimonial
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
    """车辆订阅页面，显示可用于订阅的车辆"""
    # 获取筛选参数
    pickup_location = request.GET.get('pickup_location', '')
    fuel_type = request.GET.get('fuel_type', '')
    car_category = request.GET.get('car_category', '')
    seat_number = request.GET.get('seat_number', '')
    
    # 默认使用VehicleCategory模型中的数据
    subscription_vehicles = VehicleCategory.objects.filter(
        renting_category=True,
        category_type__web_available=True
    )
    
    # 应用筛选条件
    if pickup_location:
        subscription_vehicles = subscription_vehicles.filter(
            locations__name__icontains=pickup_location
        )
    
    if fuel_type:
        subscription_vehicles = subscription_vehicles.filter(
            vehicle_type__name__icontains=fuel_type
        )
    
    if car_category:
        subscription_vehicles = subscription_vehicles.filter(
            name__icontains=car_category
        )
    
    if seat_number:
        subscription_vehicles = subscription_vehicles.filter(
            num_adults__gte=int(seat_number)
        )
    
    # 获取所有可用的取车地点
    locations = Location.objects.filter(is_airport=False)
    
    # 获取所有可用的燃料类型
    fuel_types = VehicleType.objects.all()
    
    # 获取所有可用的车辆类别
    car_categories = VehicleCategory.objects.filter(
        renting_category=True,
        category_type__web_available=True
    ).values_list('name', flat=True).distinct()
    
    # 获取所有可用的座位数
    seat_numbers = VehicleCategory.objects.filter(
        renting_category=True,
        category_type__web_available=True
    ).values_list('num_adults', flat=True).distinct().order_by('num_adults')
    
    context = {
        'subscription_vehicles': subscription_vehicles,
        'locations': locations,
        'fuel_types': fuel_types,
        'car_categories': car_categories,
        'seat_numbers': seat_numbers,
        'selected_location': pickup_location,
        'selected_fuel_type': fuel_type,
        'selected_car_category': car_category,
        'selected_seat_number': seat_number,
    }
    
    return render(request, 'pages/subscription.html', context)

def subscription_car_detail(request, make, model):
    """Subscription car detail page"""
    # For demo, use the same subscription_cars as in subscription()
    subscription_cars = [
        {
            'make': 'Hyundai',
            'model': 'Venue',
            'type': 'PETROL',
            'image_url': 'https://allpicsandvideos.blob.core.windows.net/rush-car-rental-static/images/pics/ts.jpg',
            'price_per_week': 230,
            'is_available': True,
            'is_great_value': True
        },
        {
            'make': 'Nissan',
            'model': 'X-Trail',
            'type': 'PETROL',
            'image_url': 'https://allpicsandvideos.blob.core.windows.net/rush-car-rental-static/images/pics/ns.jpg',
            'price_per_week': 260,
            'is_available': True,
            'is_great_value': False
        },
        {
            'make': 'Toyota',
            'model': 'Yaris Cross Hybrid',
            'type': 'HYBRID',
            'image_url': 'https://allpicsandvideos.blob.core.windows.net/rush-car-rental-static/images/pics/kin.jpg',
            'price_per_week': 279,
            'is_available': True,
            'is_great_value': False
        },
        {
            'make': 'Suzuki',
            'model': 'Swift',
            'type': 'PETROL',
            'image_url': 'https://allpicsandvideos.blob.core.windows.net/rush-car-rental-static/images/pics/sb.jpg',
            'price_per_week': 280,
            'is_available': True,
            'is_great_value': False
        },
        {
            'make': 'Smart',
            'model': '#1',
            'type': 'ELECTRIC',
            'image_url': 'https://allpicsandvideos.blob.core.windows.net/rush-car-rental-static/images/pics/mx.jpg',
            'price_per_week': 289,
            'is_available': True,
            'is_great_value': True
        },
        {
            'make': 'Smart',
            'model': '#3',
            'type': 'ELECTRIC',
            'image_url': 'https://allpicsandvideos.blob.core.windows.net/rush-car-rental-static/images/pics/bz.jpg',
            'price_per_week': 299,
            'is_available': True,
            'is_great_value': True
        }
    ]
    
    # 将输入转换为小写并移除连字符
    make = make.lower()
    model = model.lower().replace('-', ' ')
    
    # 特殊处理 Smart 车型
    if make == 'smart':
        if model == '1':
            model = '#1'
        elif model == '3':
            model = '#3'
    
    # 查找匹配的车辆，同时处理模型名称中的连字符
    car = next((c for c in subscription_cars if 
                c['make'].lower() == make and 
                c['model'].lower().replace('-', ' ') == model), None)
    
    if not car:
        from django.http import Http404
        raise Http404('Car not found')
        
    return render(request, 'pages/subscription_car_detail.html', {'car': car})
