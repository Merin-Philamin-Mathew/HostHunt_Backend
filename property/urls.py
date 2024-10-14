from django.urls import path
from .views import *


urlpatterns = [
    path('new-listing/property-details', PropertyDetails.as_view(),name='property_details'),
    path('new-listing/property-details/<int:pk>/', PropertyDetails.as_view(), name='update-property'),
    path('new-listing/documents', PropertyDocumentUploadView.as_view(), name='property-document-upload'),
    path('new-listing/submit_review/<int:property_id>/<str:status>/', ChangeStatus.as_view() , name='submit_review'),

    path('all-properties/', get_all_properties, name='get_all_properties'),

]