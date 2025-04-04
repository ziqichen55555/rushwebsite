from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:car_id>/', views.create_booking, name='create_booking'),
    path('options/<str:temp_booking_id>/', views.add_options, name='add_options'),
    path('confirm/<str:temp_booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
