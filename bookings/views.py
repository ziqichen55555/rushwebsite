from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Booking, AddonOption, BookingAddon
from .forms import AddonSelectionForm
from cars.models import Car
from locations.models import Location
from decimal import Decimal

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
            status='pending'  # Change to pending until addons are selected
        )
        booking.save()
        
        # Redirect to addon selection instead of directly confirming
        return redirect('select_addons', booking_id=booking.id)
    
    # If GET request, render the form with pre-filled data from the URL parameters
    return redirect('car_detail', car_id=car.id)

@login_required
def select_addons(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    available_addons = AddonOption.objects.filter(is_active=True).order_by('order', 'name')
    
    # If booking is already confirmed, redirect to success page
    if booking.status == 'confirmed':
        return redirect('booking_success', booking_id=booking.id)
    
    if request.method == 'POST':
        form = AddonSelectionForm(request.POST, addons=available_addons)
        if form.is_valid():
            selected_addons = form.get_selected_addons()
            
            # Calculate additional cost for addons
            addon_cost = Decimal('0.00')
            duration = booking.duration_days
            
            # Add selected addons to the booking
            for addon_id, quantity in selected_addons.items():
                addon = AddonOption.objects.get(pk=addon_id)
                
                # Calculate cost for this addon
                if addon.pricing_type == 'per_day':
                    item_cost = addon.price * duration * quantity
                else:  # flat_fee
                    item_cost = addon.price * quantity
                
                addon_cost += item_cost
                
                # Create BookingAddon record
                BookingAddon.objects.create(
                    booking=booking,
                    addon=addon,
                    quantity=quantity
                )
            
            # Update total cost to include addons
            booking.total_cost = booking.base_cost + addon_cost
            booking.status = 'confirmed'
            booking.save()
            
            messages.success(request, "Your booking has been confirmed!")
            return redirect('booking_success', booking_id=booking.id)
    else:
        form = AddonSelectionForm(addons=available_addons)
    
    return render(request, 'bookings/select_addons.html', {
        'booking': booking,
        'form': form,
        'addons': available_addons
    })

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
