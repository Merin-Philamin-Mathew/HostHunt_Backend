from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

# ViewSet action mappings
# changes updated
create_get_room = RoomViewSet.as_view({
    'post': 'post',
})
update_delete_room = RoomViewSet.as_view({
    'put': 'put',
    'delete': 'delete',
})

# ViewSet action mappings
crud_property_images = PropertyImageViewSet.as_view({
    'post': 'create',
    'get':'list',
    'delete': 'destroy',
})

# Router for ViewSets
router = DefaultRouter()
router.register(r'onboarding/property-images/', PropertyImageViewSet, basename='property-image')

urlpatterns = [
    # ========================= HOST MANAGEMENT =========================
    path('new-listing/property-details/', PropertyDetails.as_view(), name='property_details'),
    path('new-listing/property-details/<int:pk>/', PropertyDetails.as_view(), name='update_property'),
    path('new-listing/documents/', PropertyDocumentUploadView.as_view(), name='property_document_upload'),
    path('new-listing/submit-review/<int:property_id>/<str:status>/', ChangeStatus_Submit_Review.as_view(), name='submit_review'),
    path('new-listing/<int:property_id>/policies/', PropertyPoliciesView.as_view(), name='policies_services'),
    path('new-listing/<int:property_id>/amenities/bulk/', BulkPropertyAmenityView.as_view(), name='bulk_create_property_amenities'),

    path('onboarding/rental-apartment/', RentalApartmentCreateView.as_view(), name='rental_apartment'),
    path('onboarding/rooms/', create_get_room, name='create_get_room'),
    path('onboarding/rooms/<int:room_id>/', update_delete_room, name='update_delete_room'),
    path('property-rooms/<int:property_id>/', RoomListByPropertyView.as_view(), name='rooms_by_property'),

    path('onboarding/property-images/<int:pk>/', crud_property_images),
    path('onboarding/generate-description',get_response),
    path('onboarding/save-description/<int:property_id>/', SavePropertyDescriptionView.as_view(), name='save-description'),

    # ========================= RETRIEVING VIEWS =========================
    path('host-properties/', HostPropertyListView.as_view(), name='host_properties'),  # For request.user
    path('documents/<int:property_id>/', PropertyDocumentUploadView.as_view(), name='get_all_docs'),
    path('policies-services/<int:property_id>/', GetPoliciesServicesView.as_view(), name='get_policies_services'),

    path('property-results/', PropertyResultView.as_view(), name='property_list'),

    path('all-amenities/', AmenityListView.as_view(), name='list_all_property_amenities'),
    path('active-room-facilities/', ActiveFacilityListView.as_view(), name='active_room_facilities'),
    path('active-room-types/', ActiveRoomTypeListView.as_view(), name='active_room_types'),
    path('active-bed-types/', ActiveBedTypeView.as_view(), name='active_bed_types'),

    # ========================= USER RETRIEVING DATA FOR VIEWING =========================
    path('property-display/<int:property_id>/', PropertyDisplayView.as_view(), name='property_display'),

    # ========================= ADMIN RETRIEVING DATA FOR VIEWING =========================
    path('all-properties/', get_all_properties_basic_details, name='get_all_properties'),
    path('basic-details/<int:property_id>/', PropertyDetailView.as_view(), name='property_basic_details'),
    
]

# Add router URLs
urlpatterns += router.urls
