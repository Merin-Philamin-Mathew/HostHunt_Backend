from django.contrib import admin
from .models import Property, Amenity

# Define an admin class for CustomOwner
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["property_name", "property_type","city","postcode"]

# Define an admin class for CustomUser
class AmenityAdmin(admin.ModelAdmin):
    list_display = ["amenity_name"]

# Register the models with their respective admin classes
admin.site.register(Property, PropertyAdmin)
admin.site.register(Amenity, AmenityAdmin)
 