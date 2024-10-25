import boto3
import urllib.parse
from django.conf import settings
from django.shortcuts import get_object_or_404


from rest_framework.views import APIView
from rest_framework import status, permissions, generics, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from .models import PropertyDocument, Property, Rooms
from rest_framework.decorators import api_view, permission_classes

from .serializers import PropertySerializer, PropertyDocumentSerializer,PropertyViewSerializer,PropertyDetailedViewSerializer,RentalApartmentSerializer,RoomSerializer,RoomListSerializer_Property

from .utils import CustomPagination
from .utils import Upload_to_s3, delete_file_from_s3,delete_file_from_s3_by_url



#  =============================== PROPERTY CREATION BY HOST =============================
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
                s3_file_path = f"property_thumbnails/{data['host']}/"
                response = Upload_to_s3(image_file,s3_file_path)
                data['thumbnail_image_url'] = response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error':'Thumbnail image is required!'},status=status.HTTP_400_BAD_REQUEST)

        serializer = PropertySerializer(data=data, context={'request': request})

        if serializer.is_valid():
            property_instance = serializer.save()
            response_data = {
                'data': serializer.data,
                'property_id': property_instance.id, 
                's3_file_path' : s3_file_path,
            }
            print(response_data,"response data in property details adding view")
            return Response(response_data, status=status.HTTP_201_CREATED)
        print('10000')
        delete_file_from_s3(image_file.name)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # for updation
    def put(self, request, pk):
        data = request.data.copy()
        image_file = request.FILES.get('thumbnail_image')
        print(data)

        print('0',image_file)
        if image_file:
            try:
                print('1',image_file)
                delete_file_from_s3_by_url(data['thumbnail_image_url'])
                print('2',image_file,request.user.id)
                s3_file_path = f"property_thumbnails/{request.user.id}/"
                print('3',s3_file_path)
                response = Upload_to_s3(image_file,s3_file_path)
                print('4',response)
                data['thumbnail_image_url'] = response
                print('5', data['thumbnail_image_url'])
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            property_instance = Property.objects.get(pk=pk, host=request.user)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        print('Updating property:', property_instance)
        print('Updated data:', request.data)

        serializer = PropertySerializer(property_instance, data=data, partial=True, context={'request': request})
        
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
            print('lllllll')
            documents = PropertyDocument.objects.filter(property_id=property_id)
            if not documents.exists():
                return Response({"message": "No documents found for this property."}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = PropertyDocumentSerializer(documents, many=True)
            return Response({"property_docs":serializer.data.__len__(),"documents": serializer.data,}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, *args, **kwargs):
        property_id = request.data.get('property_id')
        files = request.FILES.getlist('files')
        serializer = PropertyDocumentSerializer(data=request.data)
        print(property_id,files)

        if not property_id:
            return Response({'error': 'Property ID is required!'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not files:
            return Response({'error': 'No files provided!'}, status=status.HTTP_400_BAD_REQUEST)

        property_instance = get_object_or_404(Property, id=property_id)

        uploaded_docs = []
        try:
            for file in files:
                print('1',file)
                s3_file_path = f"property_documents/{property_instance.host.id}/{property_instance.id}/"
                print('2',s3_file_path)
                doc_url = Upload_to_s3(file, s3_file_path)
                print('3')

                document_data = {
                    'property': property_instance.id,
                    'doc_url': doc_url,
                }
                print('4')
                serializer = PropertyDocumentSerializer(data=document_data)

       
                if serializer.is_valid():
                    print('5')
                    document_instance = serializer.save()
                    print('6')
                    uploaded_docs.append(serializer.data)
                else:
                    # If there's an error with one document, roll back by deleting the uploaded files from S3
                    print('7')
                    for uploaded_doc in uploaded_docs:
                        print('8')
                        delete_file_from_s3_by_url(uploaded_doc['doc_url'])
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print('9')

            return Response({'documents': uploaded_docs}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Final step  
class ChangeStatus_Submit_Review(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    VALID_STATUSES = ["in_review","in_progress","published"]

    def post(self, request, property_id, status):
        
        if status not in self.VALID_STATUSES:
            return Response({"error": "Invalid status."}, status=400)

        try:
            property_instance = Property.objects.get(id=property_id)
            property_instance.status = status
            property_instance.save()

            # Send notification to admin - pending
            return Response({"success": "Property submitted for review."}, status=200)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=404)


class RentalApartmentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    print('rentaleapp_createview/onboarding')
    def post(self, request):
        data = request.data
        try:
            print('rentaleapp_createview/onboarding',data)
            property = data.get('property')
            print('rentaleapp_createview/property',property)
            if not property:
                print('1/onboarding')
                return Response({'error': 'Property ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            print('36/onboarding')
            try:
                print('2/onboarding')
                property_instance = Property.objects.get(id=property)
            except Property.DoesNotExist:
                return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create a RentalApartment instance
            print('34/onboarding')
            serializer = RentalApartmentSerializer(data=data)
            if serializer.is_valid():
                print('3/onboarding')
                rental_apartment = serializer.save(property=property_instance)
                return Response({'message': 'Rental apartment created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print('room creation', request.data)
        if 'property' not in request.data:
            print('1')
            return Response({'error': 'Property field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        print('2')

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            print('3',serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, room_id=None):
        try:
            room = Rooms.objects.get(pk=room_id)
        except Rooms.DoesNotExist:
            return Response({'error': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, room_id=None):
        try:
            room = Rooms.objects.get(pk=room_id)
        except Rooms.DoesNotExist:
            return Response({'error': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)

        room.delete()
        return Response({'message': 'Room deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class RoomListByPropertyView(generics.ListAPIView):
    serializer_class = RoomListSerializer_Property
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        return Rooms.objects.filter(property=property_id)
#  =============================== PROPERTY LISTING BY HOST =============================
class HostPropertyListView(generics.ListAPIView):
    serializer_class = PropertyViewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        print('hsotlistings view ',user)
        return Property.objects.filter(host=user)
    
    

# ====================================== ADMIN MANAGEMENT ==================================
# =============================== GET ALL PROPERTY BASIC DETAILS ==================================

# function to retrieve all the properites by status in the admin side and user side for displaying
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly]) 
def get_all_properties_basic_details(request):
    status_filter = request.query_params.get('propStatus')
    pg = request.query_params.get('pg_no')
    print("Status filter:", status_filter,pg)

    if status_filter :
        properties = Property.objects.filter(status=status_filter)
    else:
        properties = Property.objects.all()

    paginator = CustomPagination()
    if status_filter == 'published':
        paginator.page_size = 5
    paginated_properties = paginator.paginate_queryset(properties, request)

    serializer = PropertyViewSerializer(paginated_properties, many=True)

    return paginator.get_paginated_response(serializer.data)


# ====================================== ADMIN MANAGEMENT ==================================
# =============================== GET ALL DETIALS OF A SINGLE PROPERTY ==================================
# for getting the all details of a single property in review for admin to review
class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyDetailedViewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        property_id = self.kwargs.get('property_id')
        try:
            return Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            raise NotFound('Property not found.')

    def get(self, request, *args, **kwargs):
        property_instance = self.get_object()
        self.check_object_permissions(request, property_instance)
        serializer = self.get_serializer(property_instance)
        return Response(serializer.data)