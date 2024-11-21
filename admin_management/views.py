
from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from property.models import Property,CustomUser,Amenity,RoomFacilities, RoomType, BedType
from .serializers import CustomUserSerializer,AmenitySerializer, RoomFacilitiesSerializer, RoomTypeSerializer, BedTypeSerializer

from property.utils import CustomPagination

from django.db.models import Q  

# ================================ADMIN PROPERTY MANAGEMENT=========================================
class AdminApproveOrRejectProperty(APIView):
    permission_classes = [permissions.IsAdminUser] 

    VALID_STATUSES = ["in_review", "verified", "rejected"]

    def patch(self, request, property_id, status):
        if status not in self.VALID_STATUSES:
            return Response({"error": "Invalid status."}, status=400)

        try:
            property_instance = Property.objects.get(id=property_id)
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
            return CustomUser.objects.filter(is_owner=True).exclude(is_staff=True)
        return CustomUser.objects.all().exclude(is_staff=True)

    def get(self, request, *args, **kwargs):
        self.pagination_class.page_size = 6  # or any other value you want to set
        return super().get(request, *args, **kwargs)

# ================================ADMIN PROPERTY CONFIGURATION=========================================
# for listing all the amenity and creating
class AmenityListCreateView(generics.ListCreateAPIView):
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination 

    def get_queryset(self):
        queryset = Amenity.objects.all().order_by('id')  # Default queryset

        search_term = self.request.query_params.get('search', None)  # Get the search term from query parameters
        if search_term:
            queryset = queryset.filter(
                Q(amenity_name__icontains=search_term) |
                Q(amenity_type__icontains=search_term)  
            )
        return queryset
    
    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)  
        return super().post(request, *args, **kwargs)
    

# RoomFacilities List and Create View
class RoomFacilitiesListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomFacilitiesSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = RoomFacilities.objects.all().order_by('id')
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(Q(facility_name__icontains=search_term))
        return queryset

# RoomType List and Create View
class RoomTypeListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = RoomType.objects.all().order_by('id')
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(Q(room_type_name__icontains=search_term))
        return queryset

# BedType List and Create View
class BedTypeListCreateView(generics.ListCreateAPIView):
    serializer_class = BedTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = BedType.objects.all().order_by('id')
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(Q(bed_type_name__icontains=search_term))
        return queryset
    

# Retrieve, update, and delete a specific amenity
class AmenityRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Amenity.objects.all().order_by('id')
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAdminUser] 


# RoomFacilities Retrieve, Update, and Destroy View
class RoomFacilitiesRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomFacilities.objects.all().order_by('id')
    serializer_class = RoomFacilitiesSerializer
    permission_classes = [permissions.IsAdminUser]

# RoomType Retrieve, Update, and Destroy View
class RoomTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RoomType.objects.all().order_by('id')
    serializer_class = RoomTypeSerializer
    permission_classes = [permissions.IsAdminUser]

# BedType Retrieve, Update, and Destroy View
class BedTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BedType.objects.all().order_by('id')
    serializer_class = BedTypeSerializer
    permission_classes = [permissions.IsAdminUser]

