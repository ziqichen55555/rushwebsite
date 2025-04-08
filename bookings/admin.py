from django.contrib import admin
from .models import Booking, BookingOption
from .models_driver import Driver

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'pickup_location', 'dropoff_location', 'pickup_date', 'return_date', 'status', 'total_cost')
    list_filter = ('status', 'pickup_location', 'dropoff_location', 'damage_waiver', 'extended_area', 'satellite_navigation')
    search_fields = ('user__username', 'car__make', 'car__model')
    date_hierarchy = 'pickup_date'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'driver_age')
        }),
        ('Car Information', {
            'fields': ('car',)
        }),
        ('Rental Details', {
            'fields': ('pickup_location', 'dropoff_location', 'pickup_date', 'return_date')
        }),
        ('Booking Status', {
            'fields': ('status', 'total_cost', 'booking_date')
        }),
        ('Options', {
            'fields': ('damage_waiver', 'extended_area', 'satellite_navigation', 'child_seats', 'additional_drivers')
        }),
    )
    readonly_fields = ('booking_date',)

class BookingOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'daily_rate', 'flat_fee', 'is_quantity_option')
    search_fields = ('name', 'description')

class DriverAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'is_primary', 'booking')
    list_filter = ('is_primary', 'country_of_residence')
    search_fields = ('first_name', 'last_name', 'email', 'license_number')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'occupation')
        }),
        ('License Information', {
            'fields': ('license_number', 'license_issued_in', 'license_expiry_date', 'license_is_lifetime')
        }),
        ('Contact Details', {
            'fields': ('phone', 'mobile', 'fax')
        }),
        ('Address', {
            'fields': ('address', 'local_address', 'city', 'state', 'postcode', 'country_of_residence')
        }),
        ('Booking Information', {
            'fields': ('booking', 'is_primary', 'mailing_list')
        }),
    )
    date_hierarchy = 'created_at'

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingOption, BookingOptionAdmin)
admin.site.register(Driver, DriverAdmin)
