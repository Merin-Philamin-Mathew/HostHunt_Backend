from rest_framework import serializers
from .models import Property,PropertyDocument,PropertyAmenity,RentalApartment,Rooms, RoomType, BedType, RoomFacilities, RoomImage, PropertyImage

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
            # 'location',
            # 'lat',
            # 'lng',
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

class PropertyAmenityCRUDSerializer(serializers.ModelSerializer):
    amenity_id = serializers.IntegerField(source="amenity.id")
    free = serializers.BooleanField(default=True)

    class Meta:
        model = PropertyAmenity
        fields = ['amenity_id', 'free']
        
# ====================onboarding process===============
# properyt/view/RentalApartmentCreateView
class RentalApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalApartment
        fields = '__all__'
        # extra_kwargs = {
        #     'booking_amount': {'min_value': 0.01}, # Ensure booking_amount is greater than 0
        # }


# property/view/RoomViewSet crud of single room of a property
class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['room', 'room_image_url']

class RoomSerializer(serializers.ModelSerializer):
    facilities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=RoomFacilities.objects.all()
    )  # You can switch to another field like `slug` if needed.
    room_images = RoomImageSerializer(many=True, required=False)

    class Meta:
        model = Rooms
        fields = [
            'id', 'room_name', 'room_type', 'is_private', 'description', 'property',
            'no_of_beds', 'no_of_rooms','booking_amount',
            'monthly_rent', 'bed_type', 'area', 'facilities', 'room_images', 'available_rooms',
        ]
        # fields = [
        #     'id', 'room_name', 'room_type', 'is_private', 'description', 'property',
        #     'no_of_beds', 'no_of_rooms', 'booking_amount_choice', 'price_per_night',
        #     'monthly_rent', 'bed_type', 'area', 'facilities', 'room_images', 'available_rooms',
        # ]

    def validate(self, data):
        if not data.get('price_per_night') and not data.get('monthly_rent'):
            raise serializers.ValidationError("Either price per night or monthly rent must be provided.")
        
        room_name = data.get('room_name')
        property_id = data.get('property')
        room_id = self.instance.id if self.instance else None  # Get the current room ID if updating

        if Rooms.objects.filter(
            room_name=room_name,
            property=property_id
        ).exclude(id=room_id).exists():
            raise serializers.ValidationError(
                f"A room with the name '{room_name}' already exists in this property."
            )
        return data
    
    def create(self, validated_data):
        facilities = validated_data.pop('facilities', [])
        room_images_data = validated_data.pop('room_images', [])
        
        is_private = validated_data.get('is_private')
        no_of_beds = validated_data.get('no_of_beds')
        no_of_rooms = validated_data.get('no_of_rooms', 1)  # Default to 1 if not provided

        if is_private:
            validated_data['available_rooms'] = no_of_beds
        else:
            validated_data['available_rooms'] = no_of_beds * no_of_rooms
        
        room = Rooms.objects.create(**validated_data)

        if facilities:
            room.facilities.set(facilities)
        
        for image_data in room_images_data:
            RoomImage.objects.create(room=room, **image_data)

        return room

    def update(self, instance, validated_data):
        facilities = validated_data.pop('facilities', None)
        room_images_data = validated_data.pop('room_images', None)

      
        # Update room fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update facilities
        if facilities is not None:
            instance.facilities.set(facilities)

        # Update room images
        if room_images_data is not None:
            instance.room_images.all().delete()  # Clear existing images
            for image_data in room_images_data:
                    RoomImage.objects.create(room=instance, **image_data)

        return instance
    

class RoomFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomFacilities
        fields = ['id', 'facility_name', 'icon']


# for getting rooms by property - onboarding form
# used in property/view/RoomListSerializer_Property
class RoomListSerializer_Property(serializers.ModelSerializer):
    room_images = RoomImageSerializer(many=True, read_only=True)
    class Meta:
        model = Rooms
        fields = ['id', 'room_name','no_of_rooms','room_images','monthly_rent'] 


# used in the user display
# can use in the fetching detiails in the onboarding room form when trying to edit
class PublishedRoomDetailedSerializer_Property(serializers.ModelSerializer):
    facilities = RoomFacilitySerializer(many=True, read_only=True)
    room_images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Rooms
        fields = [
            'id',
            'room_name',
            'room_type',
            'is_private',
            'description',
            'no_of_beds',
            'no_of_rooms',
            'price_per_night',
            'monthly_rent',
            'bed_type',
            'area',
            'facilities',
            'room_images',
        ]

# onboarding crud
class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'property_image_url', 'image_name']
    def validate(self, data):
        property = data.get('property')
        property_image_url = data.get('property_image_url')

        if PropertyImage.objects.filter(property=property, property_image_url=property_image_url).exists():
            raise serializers.ValidationError(
                "A property image with this property and image URL already exists."
            )
        return data



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

# for getting all the amenities of a property in the property detailed view
class PropertyAmenitySerializer(serializers.ModelSerializer):
    amenity_name = serializers.CharField(source='amenity.amenity_name', read_only=True)
    property = serializers.PrimaryKeyRelatedField(read_only=True)  
    class Meta:
        model = PropertyAmenity
        fields = ['property', 'amenity_name', 'free']  

# used in Property/view/PropertyDetailView
class PropertyDetailedViewSerializer(serializers.ModelSerializer):
    host = serializers.EmailField(source='host.email', read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True) 
    property_amenities = PropertyAmenitySerializer(many=True, read_only=True) 
    property_images = PropertyImageSerializer(many=True, read_only = True)
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
            'property_amenities',
            'property_images'
        ]

# extra datas 

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ['id', 'room_type_name', 'icon', 'is_active']

class BedTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedType
        fields = ['id', 'bed_type_name', 'icon', 'is_active']

class  RoomFacilitySerializer (serializers.ModelSerializer):
    class Meta:
        model = RoomFacilities
        fields = ['id', 'facility_name', 'icon', 'is_active']

