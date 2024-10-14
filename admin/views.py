from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from property.models import Property
# Create your views here.


#PROPERTY MANAGEMENT
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser]) 
def get_all_properties(request):
    # Fetch properties based on their status
    verified_properties = Property.objects.filter(status='verified')
    in_review_properties = Property.objects.filter(status='in_review')
    rejected_properties = Property.objects.filter(status='rejected')

    # If no serializer is used, return raw data
    verified_data = list(verified_properties.values())
    in_review_data = list(in_review_properties.values())
    rejected_data = list(rejected_properties.values())

    # Return the data in a structured format
    return Response({
        "verified_properties": verified_data,
        "in_review_properties": in_review_data,
        "rejected_properties": rejected_data
    })