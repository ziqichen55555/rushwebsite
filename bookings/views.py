from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from .models import Booking
from cars.models import Car
from locations.models import Location

# Dictionary to store temporary bookings
temp_bookings = {}

@login_required
def create_booking(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    
    if request.method == 'POST':
        pickup_location_id = request.POST.get('pickup_location')
        dropoff_location_id = request.POST.get('dropoff_location')
        pickup_date_str = request.POST.get('pickup_date')
        return_date_str = request.POST.get('return_date')
        driver_age = request.POST.get('driver_age')
        
        # Validate data
        errors = []
        
        if not pickup_location_id:
            errors.append("Pickup location is required")
        
        if not dropoff_location_id:
            errors.append("Drop-off location is required")
        
        try:
            pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
            if pickup_date < timezone.now().date():
                errors.append("Pickup date cannot be in the past")
        except (ValueError, TypeError):
            errors.append("Invalid pickup date")
            pickup_date = None
        
        try:
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
            if pickup_date and return_date < pickup_date:
                errors.append("Return date must be after pickup date")
        except (ValueError, TypeError):
            errors.append("Invalid return date")
            return_date = None
        
        try:
            driver_age = int(driver_age)
            if driver_age < 18:
                errors.append("Driver must be at least 18 years old")
        except (ValueError, TypeError):
            errors.append("Invalid driver age")
        
        # If there are errors, show them to the user
        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('car_detail', car_id=car.id)
        
        # Calculate total cost
        duration = (return_date - pickup_date).days
        if duration < 1:
            duration = 1
        total_cost = car.daily_rate * duration
        
        # Create a temporary booking object
        temp_booking = Booking(
            user=request.user,
            car=car,
            pickup_location=Location.objects.get(pk=pickup_location_id),
            dropoff_location=Location.objects.get(pk=dropoff_location_id),
            pickup_date=pickup_date,
            return_date=return_date,
            total_cost=total_cost,
            driver_age=driver_age,
            status='pending'  # Stay as pending until confirmed
        )
        
        # Store in temp_bookings dictionary with a unique ID
        import uuid
        booking_id = str(uuid.uuid4())
        temp_bookings[booking_id] = temp_booking
        
        # Redirect to add options page
        return redirect('add_options', temp_booking_id=booking_id)
    
    # If GET request, redirect back to car detail
    return redirect('car_detail', car_id=car.id)

@login_required
def add_options(request, temp_booking_id):
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    # Calculate base cost
    base_cost = temp_booking.car.daily_rate * temp_booking.duration_days
    
    # Define costs for each option
    context = {
        'temp_booking': temp_booking,
        'temp_booking_id': temp_booking_id,  # Pass the ID to template
        'base_cost': base_cost,
        'damage_waiver_cost': 14,  # $14 per day
        'extended_area_cost': 150,  # $150 flat fee
        'gps_cost': 5,  # $5 per day
        'child_seat_cost': 8,  # $8 per day per seat
        'additional_driver_cost': 5,  # $5 per day per driver
    }
    
    return render(request, 'bookings/add_options.html', context)

@login_required
def confirm_booking(request, temp_booking_id):
    # Get the temporary booking from storage
    temp_booking = temp_bookings.get(temp_booking_id)
    
    if not temp_booking:
        messages.error(request, "Booking session expired. Please try again.")
        return redirect('home')
    
    if request.method == 'POST':
        # Get option selections from form
        # Check for both 'true' (from JavaScript) and 'on' (from HTML checkbox)
        damage_waiver_val = request.POST.get('damage_waiver', 'false')
        damage_waiver = damage_waiver_val == 'true' or damage_waiver_val == 'on'
        
        extended_area_val = request.POST.get('extended_area', 'false')
        extended_area = extended_area_val == 'true' or extended_area_val == 'on'
        
        satellite_navigation_val = request.POST.get('satellite_navigation', 'false')
        satellite_navigation = satellite_navigation_val == 'true' or satellite_navigation_val == 'on'
        
        try:
            child_seats = int(request.POST.get('child_seats', 0))
        except ValueError:
            child_seats = 0
            
        try:
            additional_drivers = int(request.POST.get('additional_drivers', 0))
        except ValueError:
            additional_drivers = 0
            
        # Print for debugging
        print(f"Form data: damage_waiver={damage_waiver_val}, extended_area={extended_area_val}, sat_nav={satellite_navigation_val}")
        
        # Apply options to temporary booking
        temp_booking.damage_waiver = damage_waiver
        temp_booking.extended_area = extended_area
        temp_booking.satellite_navigation = satellite_navigation
        temp_booking.child_seats = child_seats
        temp_booking.additional_drivers = additional_drivers
        
        # Update total cost with options
        base_cost = temp_booking.car.daily_rate * temp_booking.duration_days
        options_cost = temp_booking.options_cost
        temp_booking.total_cost = Decimal(base_cost) + Decimal(options_cost)
        
        # Change status to confirmed
        temp_booking.status = 'confirmed'
        
        # Save the booking to the database
        temp_booking.save()
        
        # Clean up temporary booking
        booking_id = temp_booking.id
        if temp_booking_id in temp_bookings:
            del temp_bookings[temp_booking_id]
        
        messages.success(request, "Your booking has been confirmed!")
        return redirect('booking_success', booking_id=booking_id)
    
    # If not a POST request, redirect back to add options
    return redirect('add_options', temp_booking_id=temp_booking_id)

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'bookings/booking_success.html', {'booking': booking})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Your booking has been cancelled")
        return redirect('user_bookings')
    
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})
