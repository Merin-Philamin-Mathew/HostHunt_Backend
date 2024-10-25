from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from property.models import Property
# Create your views here.

from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from property.models import Property,CustomUser
from .serializers import CustomUserSerializer

from property.utils import CustomPagination

# ================================ADMIN PROPERTY MANAGEMENT=========================================
class AdminApproveOrRejectProperty(APIView):
    permission_classes = [permissions.IsAdminUser] 

    VALID_STATUSES = ["in_review", "verified", "rejected"]

    def patch(self, request, property_id, status):
        if status not in self.VALID_STATUSES:
            return Response({"error": "Invalid status."}, status=400)

        try:
            property_instance = Property.objects.get(id=property_id)
            # previous_status = property_instance.status 
            property_instance.status = status
            property_instance.save()

            # Send notification to owner - pending implementation
            # Notify the owner of the status change here

            return Response({"success": f"Property status updated to {status}."}, status=200)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=404)


# ================================ADMIN USER MANAGEMENT=========================================

class UserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    def get_queryset(self):
        if 'owners' in self.request.path:
            return CustomUser.objects.filter(is_owner=True)
        return CustomUser.objects.all()

    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = 6  # or any other value you want to set
        return super().get(request, *args, **kwargs)
