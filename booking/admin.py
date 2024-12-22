from django.contrib import admin
from .models import Bookings, BookingPayment, Rent, BookingReview

# Register your models here.
class BookingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bookings._meta.fields]

class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BookingPayment._meta.fields]

class RentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Rent._meta.fields]

class BookingReviewAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BookingReview._meta.fields]


admin.site.register(Bookings, BookingAdmin)
admin.site.register(BookingPayment, BookingPaymentAdmin)
admin.site.register(Rent, RentAdmin)
admin.site.register(BookingReview, BookingReviewAdmin)
 