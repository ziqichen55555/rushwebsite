from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rental-conditions/', views.rental_conditions, name='rental_conditions'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('complaint/', views.complaint, name='complaint'),
]
