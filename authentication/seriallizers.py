from rest_framework import serializers
from .models import CustomOwner, CustomUser
from rest_framework.exceptions import ValidationError


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomOwner
        fields = ['email', 'name', 'is_active', 'is_owner', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','name', 'email', 'is_superuser', 'is_active', 'password']
        

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'is_superuser', 'is_active', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Password is write-only

    def validate(self, data):
        # Check if the user is an admin (is_superuser = True)
        if not self.instance.is_superuser:
            raise ValidationError("User is not an admin. Access denied.")
        return data