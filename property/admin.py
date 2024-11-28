from django.contrib import admin
from .models import Property, Amenity, PropertyDocument, Rooms, RentalApartment,RoomFacilities, RoomType, BedType, PropertyAmenity, Bookings, BookingPayment

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


class RoomFacilitiesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RoomFacilities._meta.fields]

class RoomTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RoomType._meta.fields]

class BedTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BedType._meta.fields]

class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PropertyAmenity._meta.fields]

class BookingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bookings._meta.fields]

class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BookingPayment._meta.fields]

admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyDocument, ProDocAdmin)
admin.site.register(Amenity, AmenityAdmin)
admin.site.register(RentalApartment, RentalApartmentAdmin)
admin.site.register(Rooms, RoomsAdmin)
admin.site.register(RoomFacilities, RoomFacilitiesAdmin)
admin.site.register(RoomType, RoomTypeAdmin)
admin.site.register(BedType, BedTypeAdmin)
admin.site.register(PropertyAmenity, PropertyAmenityAdmin)
admin.site.register(Bookings, BookingAdmin)
admin.site.register(BookingPayment, BookingPaymentAdmin)
 