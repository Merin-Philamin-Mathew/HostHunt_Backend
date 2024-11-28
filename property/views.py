import boto3
import urllib.parse
from django.conf import settings
from django.shortcuts import get_object_or_404


from rest_framework.views import APIView
from rest_framework import status, permissions, generics, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from .models import PropertyDocument, Property, Rooms, Amenity,PropertyAmenity,RoomType,BedType,RoomFacilities, Bookings, BookingPayment
from rest_framework.decorators import api_view, permission_classes

from .serializers import PropertySerializer, PropertyDocumentSerializer,PropertyViewSerializer,PropertyDetailedViewSerializer,RentalApartmentSerializer,RoomSerializer,RoomListSerializer_Property, PropertyPoliciesSerializer,PropertyAmenityCRUDSerializer,RoomTypeSerializer,BedTypeSerializer,RoomFacilitySerializer,RoomImageSerializer
from admin_management.serializers import AmenitySerializer

from .utils import CustomPagination
from .utils import Upload_to_s3, delete_file_from_s3,delete_file_from_s3_by_url

from django.http import HttpResponseRedirect
import os, stripe



#  =============================== PROPERTY CREATION BY HOST =============================
#  STEP1 
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
                print('uploaded image successfully')
                data['thumbnail_image_url'] = response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error':'Thumbnail image is required!'},status=status.HTTP_400_BAD_REQUEST)

        serializer = PropertySerializer(data=data, context={'request': request})
        print('9000')
        if serializer.is_valid():
            print('serializer valid,5000')
            property_instance = serializer.save()
            response_data = {
                'data': serializer.data,
                'property_id': property_instance.id, 
                # 's3_file_path' : s3_file_path,
            }
            print("response data in property details adding view",response_data,)
            return Response(response_data, status=status.HTTP_201_CREATED)
        print('103000')
        delete_file_from_s3(s3_file_path,image_file.name)
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
    
# STEP2
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

# STEP3 
# policies and serivicies

class PropertyPoliciesView(APIView):
    def patch(self, request, property_id):
        try:
            property_instance = Property.objects.get(pk=property_id)
        except Property.DoesNotExist:
            return Response(
                {"detail": "Property not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if property status allows updates
        if property_instance.status in ['published', 'verified']:
            return Response(
                {"detail": "Cannot update policies for published or verified properties"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PropertyPoliciesSerializer(
            property_instance, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetPoliciesServicesView(generics.RetrieveAPIView):
   permission_classes = [permissions.IsAuthenticated]
   serializer_class = PropertyPoliciesSerializer
   lookup_field = 'pk'
   lookup_url_kwarg = 'property_id'
   queryset = Property.objects.all()

   def get_object(self):
       property_id = self.kwargs.get('property_id')
       try:
           return Property.objects.get(pk=property_id, host=self.request.user)
       except Property.DoesNotExist:
           raise NotFound(detail="Property not found or you don't have permission.")

# STEP4 
# fetchAmenityclass 
class AmenityListView(generics.ListAPIView):
    queryset = Amenity.objects.all().order_by('id') 
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticated]


# for retrieving amenities of a single property 
# for bulkcreating amenities of a single property
class BulkPropertyAmenityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, property_id):
        """Retrieve all amenities for a specific property."""
        print('Retrieving amenities for property')
        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        amenities = PropertyAmenity.objects.filter(property=property_instance)
        serializer = PropertyAmenityCRUDSerializer(amenities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, property_id):
        """Create or update amenities for a specific property, removing any others not in the request."""
        print('Processing amenities for property')

        # Get amenity IDs and free status from the request data
        amenity_ids = request.data.get("amenities_ids", [])
        free_status = request.data.get("free", False)

        # Prepare data in the expected format
        data = [{"amenity_id": amenity_id, "free": free_status} for amenity_id in amenity_ids]
        
        serializer = PropertyAmenityCRUDSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            property_instance = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        PropertyAmenity.objects.filter(property=property_instance).exclude(amenity_id__in=amenity_ids).delete()

        amenities_data = serializer.validated_data
        updated_amenities = []
        for amenity_data in amenities_data:
            amenity_id = amenity_data['amenity']['id']
            free_status = amenity_data['free']
            
            property_amenity, created = PropertyAmenity.objects.update_or_create(
                property=property_instance,
                amenity_id=amenity_id,
                defaults={'free': free_status}
            )
            updated_amenities.append(property_amenity)

        return Response({"message": "Amenities processed successfully."}, status=status.HTTP_200_OK)

    
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


# crud of single room of a property
class RoomViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        print( 'room creation', data, 'request.data')
        property_id = request.data['property']
        room_images = request.FILES.getlist('room_images')
        print('room_images',room_images)
        print('property_id',property_id)
        property_instance = get_object_or_404(Property, id=property_id)

        room_name = request.data['room_name']
       
        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            print('serializer valid',serializer)
            room_instance = serializer.save()
            uploaded_room_images = []

            try:
                for file in room_images:
                    print('1',file)
                    s3_file_path = f"room_images/{property_instance.host}/P{property_instance.id}-{room_name.replace(" ", "")}"
                    image_url = Upload_to_s3(file, s3_file_path)
                    # image_url = "https://host-hunt.s3.eu-north-1.amazonaws.com/room_images/mrnmthw19@gmail.com/P43-18SingleCoatPrivateMixedDormitoryd3.3.webp"
                    image_data = {
                        'room':room_instance.id,
                        'room_image_url':image_url
                    }
                    image_serializer = RoomImageSerializer(data=image_data)
                    if image_serializer.is_valid():
                        print('image serializer is valid')
                        print('going to save image')
                        image_serializer.save()
                        print('saved images')
                        saved_images = image_serializer.data
                        print('serializer.data',saved_images)
                    else:
                        print(image_serializer.errors)
                    uploaded_room_images.append(image_url)
                data.setlist('room_images', uploaded_room_images)  # Update room_images in data
                print('Updated data:', data)

            except Exception as e:
                print('image errors',e)
                pass
            
            response_serializer = RoomListSerializer_Property(room_instance)
            return Response(response_serializer.data, status=200)
        return Response({'error':serializer.errors},status=400)

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



class ActiveRoomTypeListView(generics.ListAPIView):
    queryset = RoomType.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RoomTypeSerializer

class ActiveBedTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        active_bed_types = BedType.objects.filter(is_active=True)
        serializer = BedTypeSerializer(active_bed_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ActiveFacilityListView(generics.ListAPIView):
    queryset = RoomFacilities.objects.all().filter(is_active=True).order_by('id') 
    serializer_class = RoomFacilitySerializer
    permission_classes = [permissions.IsAuthenticated]

# for getting details of all rooom of a single property
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


#  ======================================= USER SIDE MANAGEMENT =============================
#  =============================== DETAILED ROOM DETAILS IN USER SIDE =============================
  
class PropertyDisplayView(APIView):
    def get(self, request, property_id):
        property_instance = get_object_or_404(Property, id=property_id)
        
        property_details = PropertySerializer(property_instance).data
        policies_and_services = PropertyPoliciesSerializer(property_instance).data
        amenities = PropertyAmenityCRUDSerializer(property_instance.property_amenities.all(), many=True).data
        rooms = RoomSerializer(property_instance.rooms.all(), many=True).data
        
        # Combine the data into a single response
        response_data = {
            'property_details': property_details,
            'policies_and_services': policies_and_services,
            'amenities': amenities,
            'rooms': rooms,
        }
        return Response(response_data, status=status.HTTP_200_OK)
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
# for getting the ALL DETIALS OF A SINGLE PROPERTY in review for admin to review
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
    
# class PublishedPropertyDetailView(generics.RetrieveAPIView):
#     queryset = Property.objects.all()
#     serializer_class = PublishedPropertyDetailViewSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]

#     def get_object(self):
#         property_id = self.kwargs.get('property_id')
#         try:
#             return Property.objects.get(id=property_id)
#         except Property.DoesNotExist:
#             raise NotFound('Property not found.')

#     def get(self, request, *args, **kwargs):
#         property_instance = self.get_object()
#         self.check_object_permissions(request, property_instance)
#         serializer = self.get_serializer(property_instance)
#         return Response(serializer.data)
    

# ============================== USER SIDE PROPERTY DISPLAYS ======================================
class PropertyResultView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        city = request.query_params.get('city', None)
        if city:
            properties = Property.objects.filter(
                city__iexact=city,
                status='published'
                )
            serializer = PropertyViewSerializer(properties, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "City name not provided"}, status=status.HTTP_400_BAD_REQUEST)



from datetime import datetime

class CreatePayment(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print(request.body)
        room_id = int(request.data.get('room_id'))

        check_in_date_str = request.data.get('check_in_date')
        check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
        room = Rooms.objects.get(id=room_id)
        property_id = room.property.id
        property = Property.objects.get(id=property_id)
        image_url = property.thumbnail_image_url
        booking_amount = room.monthly_rent

        booking = Bookings.objects.create(
            user=request.user,
            host=room.property.host,  # Assuming the host is linked to the property
            room=room,
            property=property,
            check_in_date=check_in_date,
            booking_amount=booking_amount,
            booking_image_url=image_url,
            booking_status='pending'
        )
        booking_payment = BookingPayment.objects.create(
            Booking=booking,
            total_amount=booking_amount,
            status='unPaid'
        )
        print(booking,booking_payment,'fslkfslk')
        stripe.api_key = settings.STRIPE_SECRET_KEY  # Explicitly set the API key
        try:
            print(settings.STRIPE_SECRET_KEY, 'kkk')


            image_url = image_url
            line_items = [{
                            'price_data': {
                                'currency': 'inr',
                                'unit_amount': int(booking_amount * 100),  # Convert to cents for Stripe
                                'product_data': {
                                    'name': 'HostHunt',
                                    'description': 'A booking for your stay at HostHunt',  # Provide a description
                                    'images': [image_url],  # Optional, but useful for the product display
                                },
                            },
                            'quantity': 1,
                        }]

            print(line_items, 'lineee')
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                success_url=f"http://localhost:8000/property/payment-success/{booking.id}/",
                # success_url=f"http://localhost:8000/payment-success/{order.id}/",
                cancel_url=f"http://localhost:8000/payment-cancel/",
                metadata={'order_id': 10},
                # metadata={'order_id': order_id},
            )

            return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)
        # except Orders.DoesNotExist:
        #     return Response({'error': 'Order not found.'}, status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_403_FORBIDDEN)
        

class PaymentSuccess(APIView):
    permission_classes = []

    def get(self, request, pk):
        try:
            booking = Bookings.objects.get(id=pk)
            booking_payment = BookingPayment.objects.get(Booking=booking)

            # You can update the payment status here if needed
            booking_payment.status = 'paid'
            booking_payment.save()

            frontend_url = f"http://localhost:5173/trial-page/"
            return HttpResponseRedirect(frontend_url)
        
        except Bookings.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

