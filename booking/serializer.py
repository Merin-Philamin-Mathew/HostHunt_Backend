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
    class Meta:
        model = BookingReview
        fields = [
            'id',
            'booking',
            'user',
            'host',
            'property',
            'cleanliness',
            'accuracy',
            'check_in',
            'communication',
            'location',
            'value',
            'overall_rating',
            'review_text',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['user', 'host', 'property']

    def create(self, validated_data):
        booking = validated_data['booking']
        validated_data['user'] = booking.user
        validated_data['host'] = booking.host
        validated_data['property'] = booking.property
        return super().create(validated_data)
