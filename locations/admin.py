from django.contrib import admin
from .models import State, Location, CityHighlight

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'is_airport')
    list_filter = ('state', 'is_airport')
    search_fields = ('name', 'city', 'address')

admin.site.register(State)
admin.site.register(Location, LocationAdmin)
admin.site.register(CityHighlight)
