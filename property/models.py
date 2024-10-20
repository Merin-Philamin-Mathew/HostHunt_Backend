from django.db import models

from authentication.models import CustomUser

class Amenity(models.Model):
    amenity_name = models.CharField(unique=True,max_length=100)
    AMENITY_TYPE_CHOICES = [
        ('gen', 'GENERAL'),
    ]
    amenity_type = models.CharField(max_length=100, null=True, blank=True, choices=AMENITY_TYPE_CHOICES )
    icon = models.CharField(max_length=100, null=True, blank=True)  # e.g., name of an icon class
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # status flag for toggling amenities
    
    def __str__(self):
        return self.amenity_name

    
class Property(models.Model):
    # Automatic Details
    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='hostels')  # ForeignKey to Host model

    # Property Details
    PROPERTY_TYPE_CHOICES = [
        ('pg', 'PG'),
        ('rental', 'Rental'),
        ('hostel', 'Hostel'),
        ('apartment', 'Apartment'),
    ]
    property_name = models.CharField(max_length=255)
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True) #later
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postcode = models.IntegerField()
    thumbnail_image_url =  models.URLField(max_length=500)
    total_bed_rooms = models.IntegerField()
    no_of_beds = models.IntegerField()
    is_private = models.BooleanField(default=False)  # Booking the whole house like rent or apartment

    # Admin Control
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('rejected', 'Rejected'),
        ('verified', 'Verified'),
        ('ready_to_list', 'Ready to List'),
        ('published', 'Published')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    is_listed = models.BooleanField(default=False) #host can also change later

    # # Facilities
    # # amenities = models.TextField()  # Assuming it's a comma-separated string of amenities
    # amenities = models.ManyToManyField(Amenity)


    # Policies and Services
    check_in_time = models.DateTimeField(blank=True, null=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    
    SMOKING_CHOICES = [
        ('yes_everywhere', 'Yes, Everywhere'),
        ('yes_designated', 'Yes, Designated Areas'),
        ('no', 'No'),
    ]
    smoking = models.CharField(max_length=20, choices=SMOKING_CHOICES, default='no')

    pets_permit = models.BooleanField(default=False)
    drinking_permit = models.BooleanField(default=False)

    GENDER_RESTRICTION_CHOICES = [
        ('no_restriction', 'No Gender Restriction'),
        ('boys_only', 'Boys Only'),
        ('girls_only', 'Girls Only'),
    ]
    gender_restriction = models.CharField(max_length=20, choices=GENDER_RESTRICTION_CHOICES, default='no_restriction')

    visitors = models.BooleanField(default=True)
    guardian = models.BooleanField(default=False)

    child_permit = models.BooleanField(default=False)
    child_from_age = models.IntegerField(blank=True, null=True)
    child_to_age = models.IntegerField(blank=True, null=True)

    curfew = models.BooleanField(default=False)
    curfew_from_time = models.TimeField(blank=True, null=True)
    curfew_to_time = models.TimeField(blank=True, null=True)

    min_nights = models.IntegerField(blank=True, null=True)  # Lock-in period
    max_nights = models.IntegerField(blank=True, null=True)  # Optional
    notice_period = models.IntegerField(default=0)  # Days (less than min_nights)

    free_cancellation = models.BooleanField(default=False)
    cancellation_period = models.IntegerField(default=0)  # No. of days before check-in

    caution_deposit = models.IntegerField(default=0) # in Rupees

    class Meta:
        unique_together = ('host', 'property_name', 'address','property_type')

    def __str__(self):
        return self.property_name
    
class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name='property_amenities')
    free = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.amenity} - {self.status} ({self.property})"

class PropertyDocument(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    doc_url = models.URLField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.property_name}-{self.doc_url}"



