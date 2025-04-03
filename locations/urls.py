from django.urls import path
from . import views

urlpatterns = [
    path('', views.location_list, name='location_list'),
    path('city-highlights/', views.city_highlights, name='city_highlights'),
]
