from rest_framework import serializers
from .models import CustomPropertyOwner

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPropertyOwner
        fields = ['name', 'email', 'is_active', 'password']