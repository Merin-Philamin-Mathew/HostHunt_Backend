from rest_framework import serializers
from authentication.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'is_staff', 'is_superuser', 'is_owner', 'is_active_user', 'is_active_owner', 'date_joined']






