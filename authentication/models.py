
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
    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_active_owner = models.BooleanField(default=False)
    passkey = models.CharField(blank=True, null=True)
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
    

class UserProfile(models.Model):

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_pic =  models.URLField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=False) 
    date_of_birth = models.DateField(blank=True, null=True)  
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)  
    about_me = models.TextField(blank=True)  
    description_as_host = models.TextField(blank=True, null=True) 
    address = models.TextField(blank=False) 

    def __str__(self):
        return f"{self.user.username}'s profile"
    
class IdentityVerification(models.Model):
    IDENTITY_CARD_CHOICES = (
    ('passport', 'Passport'),
    ('pan', 'PAN Card'),
    ('driving_license', 'Driving License'),
    ('voter_id', 'Voter ID'),
    ('social_security', 'Social Security Card'),
    ('national_id', 'National ID'),
    ('residence_permit', 'Residence Permit'),
    ('identity_card', 'Identity Card'),
)

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    identity_card = models.CharField(max_length=50,null=True, blank=True) 
    identity_proof_number = models.CharField( choices=IDENTITY_CARD_CHOICES, max_length=100, null=True, blank=True) 
    identity_card_front_img_url =  models.URLField(max_length=500)
    identity_card_back_img_url =  models.URLField(max_length=500)


