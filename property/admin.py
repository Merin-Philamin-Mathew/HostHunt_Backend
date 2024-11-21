from django.contrib import admin
from .models import Property, Amenity, PropertyDocument, Rooms, RentalApartment,RoomFacility, RoomType, BedType, PropertyAmenity

# Define an admin class for CustomOwner
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["id","property_name","status", "property_type","city","postcode"]

# Define an admin class for CustomUser
class AmenityAdmin(admin.ModelAdmin):
    list_display = ["id","amenity_name"]

class ProDocAdmin(admin.ModelAdmin):
    list_display = ["property_id", 'doc_url']

class  RoomsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Rooms._meta.fields]

class  RentalApartmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RentalApartment._meta.fields]


class RoomFacilityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RoomFacility._meta.fields]

class RoomTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RoomType._meta.fields]

class BedTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BedType._meta.fields]

class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PropertyAmenity._meta.fields]

admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyDocument, ProDocAdmin)
admin.site.register(Amenity, AmenityAdmin)
admin.site.register(RentalApartment, RentalApartmentAdmin)
admin.site.register(Rooms, RoomsAdmin)
admin.site.register(RoomFacility, RoomFacilityAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(BedType, BedTypeAdmin)
admin.site.register(PropertyAmenity, PropertyAmenityAdmin)
 