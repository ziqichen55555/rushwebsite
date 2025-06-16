from django.contrib import admin
from .models import Car, CarCategory
from pages.models import CarFeature
class CarFeatureInline(admin.TabularInline):
    model = CarFeature
    extra = 3

class CarAdmin(admin.ModelAdmin):
    list_display = ('get_make', 'get_model', 'year', 'category', 'is_available')
    list_filter = ('category', 'is_available', 'transmission')
    search_fields = ('model__make__name', 'model__model_name', 'year')
    inlines = [CarFeatureInline]

    def get_make(self, obj):
        return obj.model.make.name if obj.model and obj.model.make else None
    get_make.short_description = 'Make'

    def get_model(self, obj):
        return obj.model.model_name if obj.model else None
    get_model.short_description = 'Model'

admin.site.register(Car, CarAdmin)
admin.site.register(CarCategory)
