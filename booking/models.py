from django.db import models

# Create your models here.

class Bookings(models.Model):
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

# from django.db.models.signals import post_save, pre_delete
# from django.dispatch import receiver 

# @receiver(post_save, sender=Bookings)
# def reduce_available_rooms(sender, instance, created, **kwargs):
#     if created and instance.room:
#         room = instance.room
#         if room.available_rooms > 0:
#             room.available_rooms -= 1
#             room.save()
#         else:
#             raise ValueError("No rooms available for booking.")

# @receiver(pre_delete, sender=Bookings)
# def restore_available_rooms(sender, instance, **kwargs):
#     if instance.room:
#         room = instance.room
#         room.available_rooms += 1
#         room.save()


