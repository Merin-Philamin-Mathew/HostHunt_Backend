from rest_framework import serializers
from .models import Property,PropertyDocument
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'property_name',
            'property_type',
            'city',
            'postcode',
            'address',
            'thumbnail_image',
            'total_bed_rooms',
            'no_of_beds',
        ]

    def create(self, validated_data):
        property_instance = Property.objects.create(**validated_data)
        return property_instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['thumbnail_image'] = instance.thumbnail_image.url if instance.thumbnail_image else None
        return rep

    def validate(self, attrs):
        host = self.context['request'].user
        property_name = attrs.get('property_name')
        address = attrs.get('address')
        property_type = attrs.get('property_type')
        
        # If we are updating (i.e., there is an instance), we should exclude the current instance from the check
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
        fields = ['id', 'property', 'file', 'upload_date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['file_url'] = instance.file.url  # Include file URL for frontend usage
        return representation
    
    
class PropertyDocumentUploadSerializer(serializers.Serializer):
    property_id = serializers.IntegerField()
    files = serializers.ListField(
        child=serializers.FileField(max_length=10000, allow_empty_file=False, use_url=False)
    )

    def create(self, validated_data):
        property_id = validated_data.get('property_id')
        property_instance = Property.objects.get(id=property_id)
        files = validated_data.pop('files')

        document_objects = []
        for file in files:
            document_object = PropertyDocument.objects.create(property=property_instance, file=file)
            document_objects.append(document_object)
        
        return document_objects
