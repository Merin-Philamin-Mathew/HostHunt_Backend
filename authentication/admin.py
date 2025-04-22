from django.contrib import admin
from .models import CustomOwner, CustomUser, IdentityVerification, UserProfile

# Define an admin class for CustomOwner
class CustomOwnerAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "id"]

# Define an admin class for CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "id"]

class IdentityVerificationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IdentityVerification._meta.fields]
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserProfile._meta.fields]

# Register the models with their respective admin classes
admin.site.register(CustomOwner, CustomOwnerAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(IdentityVerification, IdentityVerificationAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
 