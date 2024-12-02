from django.contrib import admin
from .models import Bookings, BookingPayment

# Register your models here.
class BookingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bookings._meta.fields]

class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BookingPayment._meta.fields]


admin.site.register(Bookings, BookingAdmin)
admin.site.register(BookingPayment, BookingPaymentAdmin)
 