from django.urls import path
from .views import *

urlpatterns = [

    path('create_payment/', CreatePayment.as_view(), name='property-detail'),
    path('payment-success/<int:pk>/', PaymentSuccess.as_view(), name='property-detail'),
]