from rest_framework import serializers
from .models import Property,PropertyDocument,PropertyAmenity,RentalApartment,Rooms

# serializers for adding the details in the owner side
# ================verification process==================
# step one
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'host',
            'property_name',
            'property_type',
            'city',
            'postcode',
            'address',
            'thumbnail_image_url',
            'total_bed_rooms',
            'no_of_beds',
            'status',
            'is_listed'
        ]

    def create(self, validated_data):
        property_instance = Property.objects.create(**validated_data)
        return property_instance

    def validate(self, attrs):
        host = self.context['request'].user
        property_name = attrs.get('property_name')
        address = attrs.get('address')
        property_type = attrs.get('property_type')
        
        property_instance = self.instance

        # Check if the property already exists for the host (excluding the current property in case of updates)
        property_exists = Property.objects.filter(
            host=host, 
            property_name=property_name, 
            address=address, 
            property_type=property_type
        ).exclude(pk=property_instance.pk if property_instance else None).exists()
        
        if property_exists:
            raise serializers.ValidationError("A property with this name and address already exists for this host.")
        
        return attrs

class PropertyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDocument
        fields = ['property','id', 'doc_url']


class PropertyPoliciesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Property
        fields = [
            'check_in_time', 'check_out_time', 'smoking', 'pets_permit',
            'drinking_permit', 'gender_restriction', 'visitors', 'guardian',
            'child_permit', 'child_from_age', 'child_to_age', 'curfew',
            'curfew_from_time', 'curfew_to_time', 'min_nights', 'max_nights',
            'notice_period', 'free_cancellation', 'cancellation_period',
            'caution_deposit'
        ]

    def validate(self, data):
        instance = self.instance
        
        child_permit = data.get('child_permit', instance.child_permit if instance else False)
        
        if not child_permit:
            data['child_from_age'] = None
            data['child_to_age'] = None
        elif child_permit:
            if 'child_from_age' in data or 'child_to_age' in data:
                from_age = data.get('child_from_age')
                to_age = data.get('child_to_age')
                if from_age is not None and to_age is not None and from_age > to_age:
                    raise serializers.ValidationError({
                        "child_age": "Child from age cannot be greater than to age"
                    })

        curfew = data.get('curfew', instance.curfew if instance else False)
        
        if not curfew:
            data['curfew_from_time'] = None
            data['curfew_to_time'] = None
        elif curfew:
            if 'curfew_from_time' in data or 'curfew_to_time' in data:
                from_time = data.get('curfew_from_time')
                to_time = data.get('curfew_to_time')
                if (from_time is None and to_time is not None) or (from_time is not None and to_time is None):
                    raise serializers.ValidationError({
                        "curfew_time": "Both curfew times must be provided when curfew is enabled"
                    })

        if data.get('notice_period') is not None and data.get('min_nights') is not None:
            if data['notice_period'] >= data['min_nights']:
                raise serializers.ValidationError({
                    "notice_period": "Notice period should be less than minimum nights"
                })

        if data.get('max_nights') is not None and data.get('min_nights') is not None:
            if data['max_nights'] < data['min_nights']:
                raise serializers.ValidationError({
                    "max_nights": "Maximum nights cannot be less than minimum nights"
                })

        return data


# ====================onboarding process===============
class RentalApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalApartment
        fields = '__all__'
        # extra_kwargs = {
        #     'booking_amount': {'min_value': 0.01}, # Ensure booking_amount is greater than 0
        # }


class RoomSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(read_only=True)  

    class Meta:
        model = Rooms
        fields = [
            'id', 'room_name', 'room_type', 'is_private', 'description', 'property',
            'occupancy', 'no_of_rooms', 'booking_amount_choice', 'price_per_night',
            'monthly_rent', 'bed_type', 'area'
        ]

    def create(self, validated_data):
        occupancy = validated_data.get('occupancy')
        bed_type = validated_data.get('bed_type')
        is_private = validated_data.get('is_private')
        room_type = validated_data.get('room_type')

        private_text = 'Private' if is_private else 'Shared'

        room_name = f"{occupancy} {bed_type} {private_text} {room_type}"
        validated_data['room_name'] = room_name

        return super().create(validated_data)

    def update(self, instance, validated_data):
        occupancy = validated_data.get('occupancy', instance.occupancy)
        bed_type = validated_data.get('bed_type', instance.bed_type)
        is_private = validated_data.get('is_private', instance.is_private)
        room_type = validated_data.get('room_type', instance.room_type)

        private_text = 'Private' if is_private else 'Shared'

        instance.room_name = f"{occupancy}-{bed_type}-{private_text}-{room_type}"

        return super().update(instance, validated_data)

    def validate(self, data):
        if not data.get('price_per_night') and not data.get('monthly_rent'):
            raise serializers.ValidationError("Either price per night or monthly rent must be provided.")
        return data

# for getting rooms by property
class RoomListSerializer_Property(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields = ['id', 'room_name', 'booking_amount_choice','no_of_rooms'] 


# serializer for admin management___ view -> get_all_properties
class PropertyViewSerializer(serializers.ModelSerializer):
    host = serializers.EmailField(source='host.email', read_only=True)
    class Meta:
        model = Property
        fields = [
            'id',
            'host',
            'property_name',
            'property_type',
            'city',
            'postcode',
            'address',
            'thumbnail_image_url',
            'total_bed_rooms',
            'no_of_beds',
            'status',
            'is_listed',
        ]

class PropertyAmenitySerializer(serializers.ModelSerializer):
    amenity_name = serializers.CharField(source='amenity.amenity_name', read_only=True)
    property = serializers.PrimaryKeyRelatedField(read_only=True)  
    class Meta:
        model = PropertyAmenity
        fields = ['property', 'amenity_name', 'free']  

class PropertyDetailedViewSerializer(serializers.ModelSerializer):
    host = serializers.EmailField(source='host.email', read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True) 
    property_amenities = PropertyAmenitySerializer(many=True, read_only=True)  
    class Meta:
        model = Property
        fields = [
            'id',
            'host',
            'property_name',
            'property_type',
            'description',
            'address',
            'city',
            'postcode',
            'thumbnail_image_url',
            'total_bed_rooms',
            'no_of_beds',
            'is_private',
            'status',
            'is_listed',
            'check_in_time',
            'check_out_time',
            'smoking',
            'pets_permit',
            'drinking_permit',
            'gender_restriction',
            'visitors',
            'guardian',
            'child_permit',
            'child_from_age',
            'child_to_age',
            'curfew',
            'curfew_from_time',
            'curfew_to_time',
            'min_nights',
            'max_nights',
            'notice_period',
            'free_cancellation',
            'cancellation_period',
            'caution_deposit',
            'documents',
            'property_amenities'  
        ]
