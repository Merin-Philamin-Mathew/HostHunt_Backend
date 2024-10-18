import boto3
from django.conf import settings

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import PropertyDocument, Property
from rest_framework.decorators import api_view, permission_classes

from .serializers import PropertySerializer, PropertyDocumentSerializer, PropertyDocumentUploadSerializer,PropertyViewSerializer

from .utils import CustomPagination



#  =============================== PROPERTY CREATION =============================
#  STEP 1
# for creating and updating the most mandatory property details where values cant be null
class PropertyDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #for creation
    def post(self, request):
        print(request.data,'property/propertyDetails/////////////', request.user)
        data = request.data.copy()
        data['host'] = request.user.id
        image_file = request.FILES.get('thumbnail_image')
     
        if image_file:
            # Upload the image to S3
            s3 = boto3.client('s3',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                              region_name=settings.AWS_S3_REGION_NAME)
            print(s3,'kkkkkkk')
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3_file_path = f"property_thumbnails/{request.user}/{image_file.name}"

            try:
                # Upload the file to S3
                print('going to upload to s3')
                s3.upload_fileobj(image_file, bucket_name, s3_file_path,
                                  ExtraArgs={ 'ContentType': image_file.content_type})
                print('1')
                # Get the S3 URL for the uploaded image
                image_url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_file_path}"
                print('2',image_url)
                data['thumbnail_image_url'] = image_url

            except Exception as e:
                print('3 error',e)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        serializer = PropertySerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'data': serializer.data,
                'property_id': serializer.data.id, 
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        print('error------------------', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # for updation
    def put(self, request, pk):
        print('lllllllllllllllll')
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

