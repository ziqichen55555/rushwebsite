from django.contrib import admin
from .models import Booking, BookingOption

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

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingOption, BookingOptionAdmin)
