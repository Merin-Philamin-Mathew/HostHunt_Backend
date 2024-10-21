from django.urls import path
from .views import *


urlpatterns = [
    # host management
    path('new-listing/property-details', PropertyDetails.as_view(),name='property_details'),
    path('new-listing/property-details/<int:pk>/', PropertyDetails.as_view(), name='update-property'),
    path('new-listing/documents', PropertyDocumentUploadView.as_view(), name='property-document-upload'),
    path('new-listing/submit_review/<int:property_id>/<str:status>/', ChangeStatus_Submit_Review.as_view() , name='submit_review'),

    path('host-properties/', HostPropertyListView.as_view(), name='get_host_properties'),
    path('documents/<int:property_id>/', PropertyDocumentUploadView.as_view(), name='get_all_docs'),

    # admin retrieving data for viewing
    path('all-properties/', get_all_properties_basic_details, name='get_all_properties'),
    path('basic-details/<int:property_id>/', PropertyDetailView.as_view(), name='property-detail'),

]