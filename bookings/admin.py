from django.contrib import admin
from .models import Booking, AddonOption, BookingAddon

class BookingAddonInline(admin.TabularInline):
    model = BookingAddon
    extra = 1

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'pickup_location', 'dropoff_location', 'pickup_date', 'return_date', 'status', 'total_cost')
    list_filter = ('status', 'pickup_location', 'dropoff_location')
    search_fields = ('user__username', 'car__make', 'car__model')
    date_hierarchy = 'pickup_date'
    inlines = [BookingAddonInline]

class AddonOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'pricing_type', 'is_active', 'order')
    list_filter = ('pricing_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_active', 'order')

admin.site.register(Booking, BookingAdmin)
admin.site.register(AddonOption, AddonOptionAdmin)
