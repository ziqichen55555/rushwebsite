from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('cars/', include('cars.urls')),
    path('bookings/', include('bookings.urls')),
    path('locations/', include('locations.urls')),
]
