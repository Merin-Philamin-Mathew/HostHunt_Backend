from rest_framework import serializers
from .models import Property,PropertyDocument,PropertyAmenity

# serializers for adding the details in the owner side
# till step one
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
