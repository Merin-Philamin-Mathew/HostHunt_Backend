from django.urls import path
from .views import *

urlpatterns = [
        path('property/approval/<int:property_id>/<str:status>/', AdminApproveOrRejectProperty.as_view(), name='property_approval'),

]
