from rest_framework import serializers
from .models import CustomOwner, CustomUser
from rest_framework.exceptions import ValidationError
from .models import IdentityVerification,UserProfile


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
    

class IdentityVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = [
            'user', 
            'identity_card', 
            'identity_proof_number', 
            'identity_card_front_img_url', 
            'identity_card_back_img_url',
            'status',
        ]
        
    def validate(self, data):
        # Additional custom validation if needed
        return data
   
class ProfilePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'profile_pic']
    
    def validate(self, data):
        # Additional custom validation if needed
        return data



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 
            'date_of_birth', 
            'gender', 
            'about_me', 
            'description_as_host', 
            'address'
        ]
        extra_kwargs = {
            'phone_number': {'required': True},
            'address': {'required': True}
        }






