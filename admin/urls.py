from django.urls import path
from .views import *

urlpatterns = [
        path('/all-properties/', get_all_properties, name='get_all_properties'),

]
