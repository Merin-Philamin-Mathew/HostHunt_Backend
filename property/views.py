from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import PropertyDocument, Property
from rest_framework.decorators import api_view, permission_classes

from .serializers import PropertySerializer, PropertyDocumentSerializer, PropertyDocumentUploadSerializer


#  =============================== PROPERTY CREATION =============================
#  STEP 1
# for creating and updating the most mandatory property details where values cant be null
class PropertyDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #for creation
    def post(self, request):
        print('property/propertyDetails/////////////', request.user)

        serializer = PropertySerializer(data=request.data, context={'request': request})
        print('..........serializer', serializer)
        
        # Validate and save the serializer
        if serializer.is_valid():
            print('valid serializer===========')
            property_instance = serializer.save(host=request.user)
            print('//////////dd', property_instance)
            
            # Return the serialized data, including the ID of the saved property instance
            response_data = {
                'data': PropertySerializer(property_instance).data,
                'property_id': property_instance.id,  # Include the unique ID here
            }
            print(response_data,'response......................')
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        print('error------------------', serializer.errors)
        # Return an error response if the serializer is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # for updation
    def put(self, request, pk):
        # Retrieve the property instance to update
        print('lllllllllllllllll')
        try:
            property_instance = Property.objects.get(pk=pk, host=request.user)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        print('Updating property:', property_instance)
        print('Updated data:', request.data)

        # Use the existing instance to update
        serializer = PropertySerializer(property_instance, data=request.data, partial=True, context={'request': request})
        
        # Validate and save the serializer
        if serializer.is_valid():
            updated_property_instance = serializer.save()
            print('Updated property instance:', updated_property_instance)

            # Return the serialized data, including the ID of the updated property instance
            response_data = {
                'data': PropertySerializer(updated_property_instance).data,
                'property_id': updated_property_instance.id  # Include the unique ID here
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        print('error------------------', serializer.errors)
        # Return an error response if the serializer is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# step 2
class PropertyDocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, property_id, *args, **kwargs):
        try:
            # Fetch all documents for the property
            documents = PropertyDocument.objects.filter(property_id=property_id)
            if not documents.exists():
                return Response({"message": "No documents found for this property."}, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the documents
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


