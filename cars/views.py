from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Car, CarCategory, VehicleCategory, VehicleCategoryType, VehicleFeature
from locations.models import Location
from datetime import datetime, timedelta

def car_list(request):
    category_type_id = request.GET.get('category_type', '')
    region = request.GET.get('region', '')
    pickup_location = request.GET.get('pickup_location', '')
    dropoff_location = request.GET.get('dropoff_location', '')
    pickup_date = request.GET.get('pickup_date', '')
    return_date = request.GET.get('return_date', '')
    age = request.GET.get('age', '')
    
    # Start with all vehicle categories that are available for web
    vehicles = VehicleCategory.objects.filter(
        category_type__web_available=True,
        is_available=True,
        renting_category=True
    )
    
    # Apply category type filter if provided
    if category_type_id:
        vehicles = vehicles.filter(category_type_id=category_type_id)
    
    # Apply region filter if provided
    if region:
        vehicles = vehicles.filter(region=region)
    
    # Apply location filter if provided
    if pickup_location:
        location = Location.objects.filter(name__icontains=pickup_location).first()
        if location:
            vehicles = vehicles.filter(locations=location)
    
    # Apply age filter if provided
    if age:
        try:
            driver_age = int(age)
            vehicles = vehicles.filter(age_youngest_driver__lte=driver_age)
        except (ValueError, TypeError):
            pass
    
    # Get all category types for the filter sidebar that are web available
    category_types = VehicleCategoryType.objects.filter(web_available=True)
    
    # Get all regions with available vehicles
    regions = VehicleCategory.objects.filter(
        category_type__web_available=True,
        is_available=True,
        renting_category=True
    ).values_list('region', flat=True).distinct()
    
    # Create region choices for display
    region_choices = []
    for region_code in regions:
        for choice in VehicleCategory.REGION_CHOICES:
            if choice[0] == region_code:
                region_choices.append(choice)
                break
    
    # Store search parameters for form repopulation
    search_params = {
        'pickup_location': pickup_location,
        'dropoff_location': dropoff_location,
        'pickup_date': pickup_date,
        'return_date': return_date,
        'age': age,
        'category_type': category_type_id,
        'region': region
    }
    
    return render(request, 'cars/car_list.html', {
        'vehicles': vehicles,
        'category_types': category_types,
        'region_choices': region_choices,
        'search_params': search_params
    })

def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(VehicleCategory, id=vehicle_id)
    
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
    total_cost = vehicle.daily_rate * rental_days
    
    # Get similar vehicles (same category type, different vehicles)
    similar_vehicles = VehicleCategory.objects.filter(
        category_type=vehicle.category_type,
        is_available=True,
        renting_category=True
    ).exclude(id=vehicle.id)[:3]
    
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
    
    return render(request, 'cars/vehicle_detail.html', {
        'vehicle': vehicle,
        'similar_vehicles': similar_vehicles,
        'search_params': search_params
    })

# 保留旧函数以保持兼容性
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # 如果车辆关联了新模型，重定向到新的详情页
    if car.vehicle_category:
        return vehicle_detail(request, car.vehicle_category.id)
    
    # 否则使用旧的逻辑
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
