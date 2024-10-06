from django.contrib.auth.backends import BaseBackend
from .models import CustomUser, CustomOwner

class CustomOwnerBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            owner = CustomOwner.objects.get(email=email)
            if owner.check_password(password):
                return owner
        except CustomOwner.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomOwner.objects.get(pk=user_id)
        except CustomOwner.DoesNotExist:
            return None
