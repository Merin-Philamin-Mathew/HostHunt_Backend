
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,  Permission, Group



class CustomUserManager(BaseUserManager):
    def create_user(self,email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(
            email = email, name=name, **extra_fields
        )
        user.set_password(password)
        user.save()
        return user
    
    
    def create_superuser(self, email,name, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email,name, password, **extra_fields)
    
    
class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField()
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
    Group,
    related_name='customuser_groups',  # Custom related name for regular users
    blank=True,
    help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_user_permissions',  # Custom related name for regular users
        blank=True,
        help_text='Specific permissions for this user.',
    )

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return self.is_superuser

    def __str__(self):
        return self.email
    

class CustomOwner(AbstractBaseUser):
    name = models.CharField()
    email = models.EmailField(unique=True)
    is_owner = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
    Group,
    related_name='propertyowner_groups',  # Custom related name for property owners
    blank=True,
    help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='propertyowner_user_permissions',  # Custom related name for property owners
        blank=True,
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.email