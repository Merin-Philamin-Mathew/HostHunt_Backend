import uuid
from django.db import models

# Create your models here.

class Bookings(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='bookings')
    host = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='client_bookings')
    room = models.ForeignKey('property.Rooms', on_delete=models.DO_NOTHING, related_name='bookings', blank=True, null=True)
    property = models.ForeignKey('property.Property', on_delete=models.DO_NOTHING, related_name='bookings', blank=True, null=True)
    check_in_date = models.DateField()
    booking_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_image_url = models.URLField(max_length=500)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reserved', 'Reserved'),
        ('confirmed','Confirmed'),
        ('checked_in', 'Cheched_In'),
        ('checked_out', 'Checked_Out'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    is_rent = models.BooleanField(default=False) 
    booking_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BookingPayment(models.Model):
    Booking = models.OneToOneField(Bookings, on_delete=models.CASCADE, related_name='booking_payment')
    total_amount = models.IntegerField(null=True, blank=True)
    STATUS_CHOICES = [
        ('unPaid', 'UnPaid'),
        ('paid', 'Paid'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unPaid')
    payment_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Rent(models.Model):
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE, related_name='rents')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()  # Owner-defined due date (e.g., 1st of every month)
    notification_period = models.IntegerField(default=3)  # Notify 3 days before
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rent_method = models.CharField(
        max_length=20, 
        choices=[('notificationsOnly', 'Notification Only'), ('rentThroughHostHunt', 'Rent Through HostHunt')],
        default='notificationsOnly'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BookingReview(models.Model):
    booking = models.OneToOneField(Bookings, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='user_reviews')
    host = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='host_reviews')
    property = models.ForeignKey('property.Property', on_delete=models.CASCADE, related_name='property_reviews')
    cleanliness = models.FloatField(default=0, help_text="Rating for cleanliness (0-5)")
    accuracy = models.FloatField(default=0, help_text="Rating for accuracy (0-5)")
    check_in = models.FloatField(default=0, help_text="Rating for check-in experience (0-5)")
    communication = models.FloatField(default=0, help_text="Rating for communication (0-5)")
    location = models.FloatField(default=0, help_text="Rating for location (0-5)")
    value = models.FloatField(default=0, help_text="Rating for value (0-5)")
    overall_rating = models.FloatField(default=0, help_text="Overall rating (calculated)")
    review_text = models.TextField(blank=True, null=True, help_text="Optional review text")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"Review for Booking {self.booking.id} by {self.user.name}"

class ReviewLikeDislike(models.Model):
    review = models.ForeignKey(BookingReview, on_delete=models.CASCADE, related_name='likes_dislikes')
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE)
    liked = models.BooleanField(default=True, help_text="True if the user liked the review")

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        action = "Liked" if self.liked else "Disliked"
        return f"{self.user.name} {action} Review {self.review.id}"

