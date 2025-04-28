from django.shortcuts import render
from cars.models import Car, CarCategory
from locations.models import Location, CityHighlight
from .models import Testimonial

def home(request):
    featured_cars = Car.objects.filter(is_available=True).order_by('?')[:6]
    locations = Location.objects.all()
    categories = CarCategory.objects.all()
    city_highlights = CityHighlight.objects.all()[:3]
    testimonials = Testimonial.objects.filter(is_active=True).order_by('?')[:3]
    
    context = {
        'featured_cars': featured_cars,
        'locations': locations,
        'categories': categories,
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
