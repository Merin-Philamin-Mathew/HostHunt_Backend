from django.urls import path
from .views import *

urlpatterns = [
        path('property/approval/<int:property_id>/<str:status>/', AdminApproveOrRejectProperty.as_view(), name='property_approval'),
        path('users/', UserListView.as_view(), name='user-list'),  
        path('owners/', UserListView.as_view(), name='owner-list'),  

        path('amenities', AmenityListCreateView.as_view(), name='amenity-list-create'),
        path('amenity/<int:pk>', AmenityRetrieveUpdateDestroyView.as_view(), name='amenity-detail'),

        # RoomFacilities URLs
        path('room-facilities/', RoomFacilitiesListCreateView.as_view(), name='roomfacilities-list-create'),
        path('room-facility/<int:pk>/', RoomFacilitiesRetrieveUpdateDestroyView.as_view(), name='roomfacilities-detail'),

        # RoomType URLs
        path('room-types/', RoomTypeListCreateView.as_view(), name='roomtype-list-create'),
        path('room-type/<int:pk>/', RoomTypeRetrieveUpdateDestroyView.as_view(), name='roomtype-detail'),

        # BedType URLs
        path('bed-types/', BedTypeListCreateView.as_view(), name='bedtype-list-create'),
        path('bed-type/<int:pk>/', BedTypeRetrieveUpdateDestroyView.as_view(), name='bedtype-detail'),
]
