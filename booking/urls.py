from django.urls import path
from .views import *

urlpatterns = [
# ======================BOOKING==================================
    path('create_payment/', CreatePayment.as_view()),
    path('payment-success/<int:pk>/', PaymentSuccess.as_view()),

# get booking details by id
    path('booking-details/<int:booking_id>/', BookingDetailsView.as_view(), name='booking-details'),

    path('update-status/<int:booking_id>/', UpdateBookingStatusView.as_view(), name='update-booking-status'),

# =====================RENT MANAGEMENT=====================================
    path('rents/upcoming/<int:booking_id>/', GetUpcomingRentView.as_view(), name='get-upcoming-rent'),
    path('create_rent_payment/', Create_RentPayment.as_view()),
    path('rent_payment_success/<int:pk>/', RentPaymentSuccess.as_view()),
    path('rents/paid-overdue/<int:booking_id>/', PaidAndOverdueRentsView.as_view(), name='paid-overdue-rents'),


# =====================USER MANAGEMENT=====================================
# get booking details by of a particular user
    path('userbookings/', UserBookingsView.as_view(), name='user-bookings-details'),

# =====================HOST MANAGEMENT=====================================
# get booking details by of a particular host
    path('hostbookings/', HostBookingsView.as_view(), name='host-bookings-details'),
    path('rent/', CreateRentView.as_view(), name='host-rent'),
    # Create a Review : POST
    # Retrieve All Reviews of a particulr user : GET
    path('reviews/', BookingReviewListCreateView.as_view(), name='reviews-list-create'),
    # Retrieve a Specific Review : GET
    # Update a Review : PUT         
    # Delete a Review : DELETE
    path('reviews/<int:pk>/', BookingReviewDetailView.as_view(), name='reviews-detail'),
]