from django.urls import path
from .views import *

urlpatterns = [
        path('property/approval/<int:property_id>/<str:status>/', AdminApproveOrRejectProperty.as_view(), name='property_approval'),
        path('users/', UserListView.as_view(), name='user-list'),  
        path('owners/', UserListView.as_view(), name='owner-list'),  

        path('amenities', AmenityListCreateView.as_view(), name='amenity-list-create'),
        path('amenity/<int:pk>/', AmenityRetrieveUpdateDestroyView.as_view(), name='amenity-detail'),
]
