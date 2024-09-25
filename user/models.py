
from django.db import models
from authentication.models import CustomUser

    
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    full_name = models.CharField(max_length=50)
    dob = models.DateField('2012-02-02')
    profile_pic = models.ImageField(upload_to='user/profile_pic',null=True, blank=True)

    def __str__(self):
        return str(self.full_name)
    