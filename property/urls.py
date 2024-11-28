from django.urls import path
from .views import *

create_get_room = RoomViewSet.as_view({
    'post': 'post',
    # 'get': 'get',
})
update_delete_room = RoomViewSet.as_view({
    'put': 'put',
    'delete': 'delete',
})
urlpatterns = [
# =========================HOST_MANAGEMENT=======================================
    path('new-listing/property-details', PropertyDetails.as_view(),name='property_details'),
    path('new-listing/property-details/<int:pk>/', PropertyDetails.as_view(), name='update-property'),
    path('new-listing/documents', PropertyDocumentUploadView.as_view(), name='property-document-upload'),
    path('new-listing/submit-review/<int:property_id>/<str:status>/', ChangeStatus_Submit_Review.as_view() , name='submit_review'),
    path('new-listing/<int:property_id>/policies/', PropertyPoliciesView.as_view(), name='policies-services'),
            # get and create amenities by property
    path('new-listing/<int:property_id>/amenities/bulk/', BulkPropertyAmenityView.as_view(), name='bulk-create-property-amenities'),
   
    path('onboarding/rental-appartment/', RentalApartmentCreateView.as_view() , name='rental_appartment'),
    path('onboarding/rooms/', create_get_room, name='create_get_room'),
    path('onboarding/rooms/<int:room_id>/', update_delete_room, name='update_delete_room'),

    path('property-rooms/<int:property_id>/', RoomListByPropertyView.as_view(), name='rooms_by_property'),

# retrieving views
    path('host-properties/', HostPropertyListView.as_view(), name='get_host_properties'), #request.user
    path('documents/<int:property_id>/', PropertyDocumentUploadView.as_view(), name='get_all_docs'),
    path('get-policies-services/<int:property_id>/', GetPoliciesServicesView.as_view(), name='get-policies-services'),
    
    path('property-results/', PropertyResultView.as_view(), name='property-list'),

    path('all-amenities/', AmenityListView.as_view(), name='list-all-property-amenities'),
    path('active-room-facilities/', ActiveFacilityListView.as_view(), name='active-room-facilities'),
    path('active-room-types/', ActiveRoomTypeListView.as_view(), name='active-room-types'),
    path('active-bed-types/', ActiveBedTypeView.as_view(), name='active-bed-types'),
# ====================USER RETRIEVING DATA FOR VIEWING==========================================
    path('property-display-view/<int:property_id>/', PropertyDisplayView.as_view(), name='property-detail'),
    # path('all-room-facilities/', AmenityListView.as_view(), name='list-all-property-amenities'),
# ====================ADMIN RETRIEVING DATA FOR VIEWING==========================================
    path('all-properties/', get_all_properties_basic_details, name='get_all_properties'),
    path('basic-details/<int:property_id>/', PropertyDetailView.as_view(), name='property-detail'),

    path('create_payment/', CreatePayment.as_view(), name='property-detail'),
    path('payment-success/<int:pk>/', PaymentSuccess.as_view(), name='property-detail'),
]