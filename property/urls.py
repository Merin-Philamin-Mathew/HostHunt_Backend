from django.urls import path
from .views import *


urlpatterns = [
    path('new-listing/property-details', PropertyDetails.as_view(),name='property_details'),
    path('test/', Test.as_view(),name='test'),
]