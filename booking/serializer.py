from rest_framework import serializers
from .models import Bookings,  Rent,BookingReview

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'

class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = '__all__'





class BookingReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    property_name = serializers.SerializerMethodField()

    class Meta:
        model = BookingReview
        fields = [
            'id',
            'booking',
            'user',
            'user_name',  # Add the user's name to the output
            'property_name',
            'host',
            'property',
            'cleanliness',
            'accuracy',
            'check_in',
            'communication',
            'location',
            'review_replay',
            'value',
            'overall_rating',
            'review_text',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['user', 'host', 'property']

    def get_user_name(self, obj):
        """Fetch the username of the reviewer."""
        return obj.user.name if obj.user else None
    
    def get_property_name(self, obj):
        """Fetch the username of the reviewer."""
        return obj.property.property_name if obj.property else None

    def create(self, validated_data):
        booking = validated_data['booking']
        validated_data['user'] = booking.user
        validated_data['host'] = booking.host
        validated_data['property'] = booking.property
        return super().create(validated_data)
