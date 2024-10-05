from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response



# Create your views here.

class PropertyDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Ensure the user has the 'owner' role
        if request.user.role != 'owner':
            return Response({'detail': 'Unauthorized - You must be an owner'}, status=status.HTTP_403_FORBIDDEN)

        print('property/property_details', request.data)
        return Response({'data': request.data})
