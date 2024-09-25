from rest_framework import serializers
from .models import CustomOwner, CustomUser

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomOwner
        fields = ['email', 'name', 'is_active', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'is_superuser', 'password']