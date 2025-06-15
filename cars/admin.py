from django.contrib import admin
from .models import Car, CarCategory
from pages.models import CarFeature
class CarFeatureInline(admin.TabularInline):
    model = CarFeature
    extra = 3

class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'category', 'is_available')
    list_filter = ('category', 'is_available', 'transmission')
    search_fields = ('make', 'model', 'year')
    inlines = [CarFeatureInline]

admin.site.register(Car, CarAdmin)
admin.site.register(CarCategory)
