from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Booking
from cars.models import Car
from locations.models import Location

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
            if return_date < pickup_date:
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
        
        # Create booking
        booking = Booking(
            user=request.user,
            car=car,
            pickup_location=Location.objects.get(pk=pickup_location_id),
            dropoff_location=Location.objects.get(pk=dropoff_location_id),
            pickup_date=pickup_date,
            return_date=return_date,
            total_cost=total_cost,
            driver_age=driver_age,
            status='confirmed'  # Auto-confirm for simplicity
        )
        booking.save()
        
        messages.success(request, "Your booking has been confirmed!")
        return redirect('booking_success', booking_id=booking.id)
    
    # If GET request, render the form with pre-filled data from the URL parameters
    return redirect('car_detail', car_id=car.id)

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
