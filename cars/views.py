from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Car, CarCategory
from locations.models import Location
from datetime import datetime, timedelta

def car_list(request):
    category_filter = request.GET.get('category', '')
    pickup_location = request.GET.get('pickup_location', '')
    dropoff_location = request.GET.get('dropoff_location', '')
    pickup_date = request.GET.get('pickup_date', '')
    return_date = request.GET.get('return_date', '')
    age = request.GET.get('age', '')
    
    # Start with all cars
    cars = Car.objects.filter(is_available=True)
    
    # Apply category filter if provided
    if category_filter:
        cars = cars.filter(category__name=category_filter)
    
    # Apply location filter if provided
    if pickup_location:
        location = Location.objects.filter(name__icontains=pickup_location).first()
        if location:
            cars = cars.filter(locations=location)
    
    # Get all car categories for the filter sidebar
    categories = CarCategory.objects.all()
    
    # Store search parameters for form repopulation
    search_params = {
        'pickup_location': pickup_location,
        'dropoff_location': dropoff_location,
        'pickup_date': pickup_date,
        'return_date': return_date,
        'age': age,
        'category': category_filter
    }
    
    return render(request, 'cars/car_list.html', {
        'cars': cars,
        'categories': categories,
        'search_params': search_params
    })

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Get search parameters from GET or set defaults
    pickup_location = request.GET.get('pickup_location', '')
    dropoff_location = request.GET.get('dropoff_location', '')
    pickup_date = request.GET.get('pickup_date', '')
    return_date = request.GET.get('return_date', '')
    age = request.GET.get('age', '')
    
    # Calculate rental duration if dates are provided
    rental_days = 1
    if pickup_date and return_date:
        try:
            start_date = datetime.strptime(pickup_date, '%Y-%m-%d')
            end_date = datetime.strptime(return_date, '%Y-%m-%d')
            rental_days = (end_date - start_date).days
            if rental_days < 1:
                rental_days = 1
        except ValueError:
            rental_days = 1
    
    # Calculate total cost
    total_cost = car.daily_rate * rental_days
    
    # Search parameters for booking form
    search_params = {
        'pickup_location': pickup_location,
        'dropoff_location': dropoff_location,
        'pickup_date': pickup_date,
        'return_date': return_date,
        'age': age,
        'rental_days': rental_days,
        'total_cost': total_cost
    }
    
    return render(request, 'cars/car_detail.html', {
        'car': car,
        'search_params': search_params
    })
