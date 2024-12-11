from django.urls import path
from .views import *

urlpatterns = [
# ======================BOOKING==================================
    path('create_payment/', CreatePayment.as_view(), name='property-detail'),
    path('payment-success/<int:pk>/', PaymentSuccess.as_view(), name='property-detail'),

# get booking details by id
    path('booking-details/<int:booking_id>/', BookingDetailsView.as_view(), name='booking-details'),

    path('update-status/<int:booking_id>/', UpdateBookingStatusView.as_view(), name='update-booking-status'),
# =====================USER MANAGEMENT=====================================
# get booking details by of a particular user
    path('userbookings/', UserBookingsView.as_view(), name='user-bookings-details'),

# =====================HOST MANAGEMENT=====================================
# get booking details by of a particular host
    path('hostbookings/', hostBookingsView.as_view(), name='host-bookings-details'),

]