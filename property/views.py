import boto3
import urllib.parse
from django.conf import settings

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import PropertyDocument, Property
from rest_framework.decorators import api_view, permission_classes

from .serializers import PropertySerializer, PropertyDocumentSerializer, PropertyDocumentUploadSerializer,PropertyViewSerializer

from .utils import CustomPagination
from .utils import Upload_to_s3, delete_file_from_s3



#  =============================== PROPERTY CREATION =============================
#  STEP 1
# for creating and updating the most mandatory property details where values cant be null
class PropertyDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #for creation
    def post(self, request):
        data = request.data.copy()
        data['host'] = request.user.id
        image_file = request.FILES.get('thumbnail_image')
     
        if image_file:
            try:
                s3_file_path = f"property_thumbnails/{data['host']}/{data['property_name']}/"
                response = Upload_to_s3(image_file,s3_file_path)
                data['thumbnail_image_url'] = response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = PropertySerializer(data=data, context={'request': request})

        if serializer.is_valid():
            property_instance = serializer.save()
            response_data = {
                'data': serializer.data,
                'property_id': property_instance.id,  
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        print('10000')
        delete_file_from_s3(s3_file_path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # for updation
    def put(self, request, pk):
        print('lllllllllllllllll')
        data = request.data.copy()
        image_file = request.FILES.get('thumbnail_image')

        s3_file_path = f"property_thumbnails/{request.user.id}/{data['property_name']}/{image_file.name}"
        if image_file != s3_file_path:
            try:
                response = Upload_to_s3(image_file,s3_file_path)
                data['thumbnail_image_url'] = response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            property_instance = Property.objects.get(pk=pk, host=request.user)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        print('Updating property:', property_instance)
        print('Updated data:', request.data)

        serializer = PropertySerializer(property_instance, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            updated_property_instance = serializer.save()
            print('Updated property instance:', updated_property_instance)

            response_data = {
                'data': PropertySerializer(updated_property_instance).data,
                'property_id': updated_property_instance.id  
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        print('error------------------', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# step 2
class PropertyDocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, property_id, *args, **kwargs):
        try:
            documents = PropertyDocument.objects.filter(property_id=property_id)
            if not documents.exists():
                return Response({"message": "No documents found for this property."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = PropertyDocumentSerializer(documents, many=True)
            return Response({"documents": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, *args, **kwargs):
        print('///////////////////',request.data)
        serializer = PropertyDocumentUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            documents = serializer.save()  # Save all the documents
            return Response({"message": "Documents uploaded successfully!", "data": [doc.file.url for doc in documents]}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 
class ChangeStatus(APIView):
    def post(self, request, property_id, status):
        try:
            property_instance = Property.objects.get(id=property_id)
            property_instance.status = status
            property_instance.save()

            # Send notification to admin if needed
            return Response({"success": "Property submitted for review."}, status=200)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=404)


# =============================== All PROPERTIES ==================================

# function to retrieve all the properites in the admin side and user side for displaying
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser]) 
def get_all_properties(request):
    status_filter = request.query_params.get('propStatus')
    pg = request.query_params.get('pg_no')
    print("Status filter:", status_filter,pg)

    if status_filter :
        properties = Property.objects.filter(status=status_filter)
    else:
        properties = Property.objects.all()

    paginator = CustomPagination()
    paginated_properties = paginator.paginate_queryset(properties, request)

    serializer = PropertyViewSerializer(paginated_properties, many=True)

    return paginator.get_paginated_response(serializer.data)

