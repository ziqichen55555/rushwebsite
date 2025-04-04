from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rental-conditions/', views.rental_conditions, name='rental_conditions'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('complaint/', views.complaint, name='complaint'),
    path('pickup-guidelines/', views.pickup_guidelines, name='pickup_guidelines'),
    path('return-guidelines/', views.return_guidelines, name='return_guidelines'),
    path('about-us/', views.about_us, name='about_us'),
]
