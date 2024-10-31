from rest_framework import serializers
from authentication.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'is_staff', 'is_superuser', 'is_owner', 'is_active_user', 'is_active_owner', 'date_joined']


from property.models import Amenity

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        # fields = ['id', 'amenity_name', 'amenity_type', 'icon', 'is_premium', 'is_active']
        fields = ['id', 'amenity_name',  'is_active']




