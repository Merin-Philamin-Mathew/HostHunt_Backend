from django.contrib import admin
from .models import CustomOwner, CustomUser

# Define an admin class for CustomOwner
class CustomOwnerAdmin(admin.ModelAdmin):
    list_display = ["name", "email"]

# Define an admin class for CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["name", "email"]

# Register the models with their respective admin classes
admin.site.register(CustomOwner, CustomOwnerAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
 