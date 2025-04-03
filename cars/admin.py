from django.contrib import admin
from .models import Car, CarCategory, CarFeature

class CarFeatureInline(admin.TabularInline):
    model = CarFeature
    extra = 3

class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'category', 'daily_rate', 'is_available')
    list_filter = ('category', 'is_available', 'transmission', 'air_conditioning')
    search_fields = ('make', 'model', 'year')
    inlines = [CarFeatureInline]

admin.site.register(Car, CarAdmin)
admin.site.register(CarCategory)
