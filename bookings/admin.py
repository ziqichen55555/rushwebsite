from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'pickup_location', 'dropoff_location', 'pickup_date', 'return_date', 'status', 'total_cost')
    list_filter = ('status', 'pickup_location', 'dropoff_location')
    search_fields = ('user__username', 'car__make', 'car__model')
    date_hierarchy = 'pickup_date'

admin.site.register(Booking, BookingAdmin)
