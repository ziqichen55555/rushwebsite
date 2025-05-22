from django.shortcuts import render
from cars.models import Car, CarCategory, VehicleCategory, VehicleCategoryType
from locations.models import Location, CityHighlight
from .models import Testimonial

def home(request):
    # 首先尝试使用新的车辆模型
    featured_vehicles = VehicleCategory.objects.filter(
        is_available=True, 
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
    vehicle_type = request.GET.get('type', '')
    
    # 默认使用VehicleCategory模型中的数据
    subscription_vehicles = VehicleCategory.objects.filter(is_available=True)
    
    # 应用筛选条件
    if vehicle_type and vehicle_type != 'all':
        subscription_vehicles = subscription_vehicles.filter(
            vehicle_type__name__icontains=vehicle_type
        )
    
    # 创建示例订阅车辆数据（模拟数据）
    subscription_cars = [
        {
            'make': 'Hyundai',
            'model': 'Venue',
            'type': 'PETROL',
            'image_url': '/static/images/subscription/hyundai-venue.jpg',
            'price_per_week': 230,
            'is_available': True,
            'is_great_value': True
        },
        {
            'make': 'Nissan',
            'model': 'X-Trail',
            'type': 'PETROL',
            'image_url': '/static/images/subscription/nissan-xtrail.jpg',
            'price_per_week': 260,
            'is_available': True,
            'is_great_value': False
        },
        {
            'make': 'Toyota',
            'model': 'Yaris Cross Hybrid',
            'type': 'HYBRID',
            'image_url': '/static/images/subscription/toyota-yaris.jpg',
            'price_per_week': 279,
            'is_available': True,
            'is_great_value': False
        },
        {
            'make': 'Suzuki',
            'model': 'Swift',
            'type': 'PETROL',
            'image_url': '/static/images/subscription/suzuki-swift.jpg',
            'price_per_week': 280,
            'is_available': True,
            'is_great_value': False
        },
        {
            'make': 'Smart',
            'model': '#1',
            'type': 'ELECTRIC',
            'image_url': '/static/images/subscription/smart-1.jpg',
            'price_per_week': 289,
            'is_available': True,
            'is_great_value': True
        },
        {
            'make': 'Smart',
            'model': '#3',
            'type': 'ELECTRIC',
            'image_url': '/static/images/subscription/smart-3.jpg',
            'price_per_week': 299,
            'is_available': True,
            'is_great_value': True
        }
    ]
    
    # 可用筛选选项
    filter_options = ['ALL', 'PETROL', 'HYBRID', 'ELECTRIC']
    
    context = {
        'subscription_cars': subscription_cars,
        'vehicle_type': vehicle_type if vehicle_type else 'ALL',
        'filter_options': filter_options
    }
    
    return render(request, 'pages/subscription.html', context)
