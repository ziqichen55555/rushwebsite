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
