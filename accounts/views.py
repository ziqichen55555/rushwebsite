from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, ProfileDriverForm
from .models import Profile
from bookings.models import Booking, Driver
import logging

# Create a logger for formal logging
logger = logging.getLogger(__name__)


@csrf_exempt
def register(request):
    logger.info("A new account registration attempt has commenced.")
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            logger.info(
                f"User {username} has successfully registered and joined the system."
            )
            messages.success(
                request, f'Account created for {username}! You can now log in')
            return redirect('login')
        else:
            logger.warning("Form validation failed during registration.")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@csrf_exempt
def profile(request):
    logger.info(
        f"User {request.user.username} is attempting to update their profile.")
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST,
                                         instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            logger.info(
                f"User {request.user.username} has updated their profile successfully."
            )
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            logger.warning(
                "Profile update operation failed due to form validation errors."
            )
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    # Retrieve drivers associated with the user
    user_drivers = request.user.profile.drivers.all()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_drivers': user_drivers
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@csrf_exempt
def add_driver(request):
    """Add new driver information to the user profile"""
    logger.info(
        f"User {request.user.username} is attempting to add new driver information."
    )

    if request.method == 'POST':
        form = ProfileDriverForm(request.POST)
        if form.is_valid():
            # Create but do not save immediately, requires handling of primary driver status
            driver = form.save(commit=False)
            driver.save()  # Save now to obtain ID

            # If set as primary, remove primacy from others
            is_primary = form.cleaned_data.get('is_primary')
            profile = request.user.profile

            if is_primary:
                # Remove primary tag from other drivers
                profile.drivers.filter(is_primary=True).update(
                    is_primary=False)
                driver.is_primary = True
                driver.save()

            # Add driver to user profile
            profile.drivers.add(driver)
            logger.info(
                f"User {request.user.username} added new driver information: {driver.get_full_name()}."
            )

            messages.success(
                request,
                f'Driver information "{driver.get_full_name()}" has been added to your profile!'
            )
            return redirect('profile')
    else:
        # Prefill email and names if available
        initial_data = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_primary': True,
            'country_of_residence': 'Australia'
        }
        form = ProfileDriverForm(initial=initial_data)

    context = {'form': form, 'title': 'Add Driver Information'}
    return render(request, 'accounts/driver_form.html', context)


@login_required
@csrf_exempt
def edit_driver(request, driver_id):
    """Edit driver information in the user profile"""
    driver = get_object_or_404(Driver, id=driver_id)

    # Ensure the user can only edit their own driver information
    if driver not in request.user.profile.drivers.all():
        messages.error(
            request,
            "You don't have permission to edit this driver information.")
        return redirect('profile')

    if request.method == 'POST':
        form = ProfileDriverForm(request.POST, instance=driver)
        if form.is_valid():
            # Save but do not commit immediately, primary driver status needs handling
            updated_driver = form.save(commit=False)

            is_primary = form.cleaned_data.get('is_primary')
            profile = request.user.profile

            if is_primary:
                # Remove primary tag from other drivers
                profile.drivers.filter(is_primary=True).exclude(
                    id=driver_id).update(is_primary=False)
                updated_driver.is_primary = True

            updated_driver.save()
            logger.info(
                f"User {request.user.username} updated driver information: {updated_driver.get_full_name()}."
            )

            messages.success(
                request,
                f'Driver information "{updated_driver.get_full_name()}" has been updated!'
            )
            return redirect('profile')
    else:
        form = ProfileDriverForm(instance=driver)

    context = {
        'form': form,
        'driver': driver,
        'title': 'Edit Driver Information'
    }
    return render(request, 'accounts/driver_form.html', context)


@login_required
def delete_driver(request, driver_id):
    """Delete driver information from the user profile"""
    driver = get_object_or_404(Driver, id=driver_id)

    # Ensure the user can only delete their own driver information
    if driver not in request.user.profile.drivers.all():
        messages.error(
            request,
            "You don't have permission to delete this driver information.")
        return redirect('profile')

    driver_name = driver.get_full_name()

    # Confirm delete if it's a POST request
    if request.method == 'POST':
        # Remove the driver from the profile
        request.user.profile.drivers.remove(driver)

        # If not associated with other Profiles and no Booking, delete completely
        if not driver.profiles.exists() and driver.booking is None:
            driver.delete()
            logger.info(
                f"Driver information {driver_name} has been permanently deleted."
            )

        messages.success(
            request,
            f'Driver information "{driver_name}" has been removed from your profile.'
        )
        return redirect('profile')

    # If it's a GET request, display confirmation page
    context = {'driver': driver}
    return render(request, 'accounts/confirm_delete_driver.html', context)


@login_required
@csrf_exempt
def user_bookings(request):
    logger.info(
        f"User {request.user.username} is reviewing their booking history.")
    bookings = Booking.objects.filter(
        user=request.user).order_by('-booking_date')
    if not bookings:
        logger.warning(f"User {request.user.username} has no booking history.")
    return render(request, 'accounts/bookings.html', {'bookings': bookings})
