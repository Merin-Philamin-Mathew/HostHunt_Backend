from rest_framework import serializers
from authentication.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'is_staff', 'is_superuser', 'is_owner', 'is_active', 'is_active_owner', 'date_joined']


from property.models import Amenity, RoomFacilities, RoomType, BedType

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'amenity_name', 'amenity_type', 'icon', 'is_premium', 'is_active']

class RoomFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomFacilities
        fields = ['id', 'facility_name', 'icon', 'is_active']

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'room_type_name', 'icon', 'is_active']

class BedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedType
        fields = ['id', 'bed_type_name', 'icon', 'is_active']