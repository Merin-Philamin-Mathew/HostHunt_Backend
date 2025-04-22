from django.conf import settings

from datetime import datetime
from rest_framework import permissions,status,generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.pagination import PageNumberPagination


from django.http import HttpResponseRedirect
from django.utils.timezone import now
import os, stripe
from .models import Bookings, BookingPayment,  Rent, BookingReview
from property.models import Rooms, Property
from .serializer import BookingSerializer, RentSerializer,BookingReviewSerializer

from django.http import JsonResponse
from web_sockets.utils import send_user_notification
from asgiref.sync import async_to_sync

from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q


FRONTEND_BASE_URL = settings.FRONTEND_BASE_URL
BACKEND_BASE_URL = settings.BACKEND_BASE_URL
class CreatePayment(APIView):
    permission_classe = [permissions.IsAuthenticated]

    def post(self, request):
        print(request.body)
        room_id = int(request.data.get('room_id'))

        check_in_date_str = request.data.get('check_in_date')
        check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
        room = Rooms.objects.get(id=room_id)
        property_id = room.property.id
        property = Property.objects.get(id=property_id)
        image_url = property.thumbnail_image_url
        booking_amount = room.monthly_rent

        booking = Bookings.objects.create(
            user=request.user,
            host=room.property.host, 
            room=room,
            property=property,
            check_in_date=check_in_date,
            booking_amount=booking_amount,
            booking_image_url=image_url,
            booking_status='pending'
        )
        booking_payment = BookingPayment.objects.create(
            Booking=booking,
            total_amount=booking_amount,
            status='unPaid'
        )
        stripe.api_key = settings.STRIPE_SECRET_KEY  # Explicitly set the API key
        try:


            image_url = image_url
            line_items = [{
                            'price_data': {
                                'currency': 'inr',
                                'unit_amount': int(booking_amount * 100), 
                                'product_data': {
                                    'name': 'HostHunt',
                                    'description': 'A booking for your stay at HostHunt',  
                                    'images': [image_url], 
                                },
                            },
                            'quantity': 1,
                        }]

            print(line_items, 'lineee')
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                success_url=f"{BACKEND_BASE_URL}/booking/payment-success/{booking.id}/",
                cancel_url=f"{BACKEND_BASE_URL}/payment-cancel/",
                metadata={'order_id': booking.id},
            )

            return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_403_FORBIDDEN)
        

class PaymentSuccess(APIView):
    permission_classes = []

    def get(self, request, pk):
        try:
            booking = Bookings.objects.get(id=pk)
            booking_payment = BookingPayment.objects.get(Booking=booking)

            booking.booking_status = 'reserved'
            booking.save()
            room = booking.room  
       
            print('Available rooms before:', room.available_rooms)
            if room.available_rooms > 0:  
                room.available_rooms -= 1
                room.save() 
                print('Available rooms after:', room.available_rooms)
            else:
                return Response({'error': 'No available rooms'}, status=status.HTTP_400_BAD_REQUEST)

            booking_payment.status = 'paid'
            booking_payment.save()

            owner_id = room.property.host.id
            message = f"A new booking has been made for your property: {room.property.property_name}."
            print('going to sent notification to other property owner')
            async_to_sync(send_user_notification)(user_id=owner_id, message=message, type='booking', senderId=booking.user.id)

            print('notification sent from the payment success view')

            frontend_url = f"{FRONTEND_BASE_URL}/account/my-stays?booking_id={pk}"
            return HttpResponseRedirect(frontend_url)
        
        except Bookings.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, booking_id):
        try:
            # Fetch the booking based on the ID
            booking = Bookings.objects.select_related('property', 'room').get(id=booking_id)
            print('1')
            # Check if the user is authorized to view the booking
            if booking.user != request.user and booking.host != request.user:
                print('2')
                return Response(
                    {"error": "You do not have permission to view this booking."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Construct the detailed booking data
            data = {
                "booking_id": booking.id,
                "check_in_date": booking.check_in_date,
                "booking_amount": booking.booking_amount,
                "booking_status": booking.booking_status,
                "booking_date": booking.booking_date,
                "booking_image": booking.booking_image_url,
                "is_rent":booking.is_rent,
                "hostel_details": {
                    "name": booking.property.property_name if booking.property else None,
                    "location": booking.property.city if booking.property else None,
                },
                "room_details": {
                    "name": booking.room.room_name if hasattr(booking.room, 'room_name') else None,
                    "monthly_rent": booking.room.monthly_rent if hasattr(booking.room, 'monthly_rent') else None,
                },
                "user_details": {
                    "name": booking.user.name,  # Assuming the user model has a user field
                    "email": booking.user.email,    # Assuming the user model has an email field
                },
                "host_details": {
                    "name": booking.host.name,  # Assuming the host model has a hostname field
                    "email": booking.host.email,    # Assuming the host model has an email field
                },
                 "reviews": {
                    "review_id": booking.review.id if hasattr(booking, 'review') else None,
                    "cleanliness": booking.review.cleanliness if hasattr(booking, 'review') else None,
                    "accuracy": booking.review.accuracy if hasattr(booking, 'review') else None,
                    "check_in": booking.review.check_in if hasattr(booking, 'review') else None,
                    "communication": booking.review.communication if hasattr(booking, 'review') else None,
                    "location": booking.review.location if hasattr(booking, 'review') else None,
                    "value": booking.review.value if hasattr(booking, 'review') else None,
                    "overall_rating": booking.review.overall_rating if hasattr(booking, 'review') else None,
                    "review_text": booking.review.review_text if hasattr(booking, 'review') else None,
                    "review_replay": booking.review.review_replay if hasattr(booking, 'review') else None,
                    "created_at": booking.review.created_at if hasattr(booking, 'review') else None,
                } if hasattr(booking, 'review') else None,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Bookings.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
         

# =========================== HOST MANAGEMENT ==================================
class HostBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensures the user is authenticated

    def get(self, request):
        user = request.user
        print(user)
        bookings = (
            Bookings.objects
            .filter(host=user)
            .exclude(booking_status='pending')
            .order_by('-id')
            .select_related('property', 'room')
        )
        data = []

        for booking in bookings:
            data.append({
                "booking_id": booking.id,
                "check_in_date": booking.check_in_date,
                "booking_amount": booking.booking_amount,
                "booking_status": booking.booking_status,
                "booking_date": booking.booking_date,
                "booking_image": booking.booking_image_url,
                "booked_by":booking.user.name,
                "is_rent":booking.is_rent,
                "hostel_details": {
                    "name": booking.property.property_name if booking.property else None,
                    "city": booking.property.city if booking.property else None,
                    # Add other fields from the property model if needed
                },
                "room_details": {
                    "name": booking.room.room_name if hasattr(booking.room, 'room_name') else None,
                }
            })

        return Response(data, status=200)
    

class UpdateBookingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def put(self, request, booking_id):
        """
        Update the booking status for the given booking ID.
        """
        try:
            # Get the booking instance
            booking = Bookings.objects.get(id=booking_id)
            print(booking_id,'entered to updating view')
            print(booking,'entered to updating view')
            # Check if the user is authorized (either the user or the host can update the status)
            if request.user != booking.user and request.user != booking.host:
                return Response(
                    {"error": "You do not have permission to update this booking."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            print('=============================================')

            # Get the new status from the request data
            new_status = request.data.get("booking_status")
            print(new_status,'=============================================')
            if not new_status or new_status not in dict(Bookings.STATUS_CHOICES).keys():
                return Response(
                    {"error": "Invalid or missing booking status."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update the booking status
            booking.booking_status = new_status
            booking.save()

            return Response(
                {"message": "Booking status updated successfully.", "new_status": booking.booking_status},
                status=status.HTTP_200_OK
            )
        except Bookings.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================USER MANAGEMENT================================
class UserBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensures the user is authenticated

    def get(self, request):
        user = request.user
        print(user)
        bookings = (
            Bookings.objects
            .filter(user=user)            
            .exclude(booking_status='pending')
            .order_by('-id')
            .select_related('property', 'room')
        )
        data = []

        for booking in bookings:
            data.append({
                "booking_id": booking.id,
                "check_in_date": booking.check_in_date,
                "booking_amount": booking.booking_amount,
                "booking_status": booking.booking_status,
                "booking_date": booking.booking_date,
                "booking_image": booking.booking_image_url,
                "hostel_details": {
                    "name": booking.property.property_name if booking.property else None,
                    "location": booking.property.city if booking.property else None,
                    # Add other fields from the property model if needed
                },
                "room_details": {
                    "name": booking.room.room_name if hasattr(booking.room, 'room_name') else None,
                }
            })

        return Response(data, status=200)

# creating and viewing and editing single reviews by booking_id if id is passed through the url
class BookingReviewListCreateView(generics.ListCreateAPIView):
 
    serializer_class = BookingReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookingReview.objects.filter(user=self.request.user)
    

    def perform_create(self, serializer):
        serializer.save()

# publicly viewing reviews
class ReviewPagination(PageNumberPagination):
    page_size = 3  # Default number of reviews per page
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        """
        Validate and retrieve the page size from the query parameters.
        If not provided, fall back to the default value.
        """
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size is not None:
            try:
                page_size = int(page_size)
                if page_size > self.max_page_size:
                    page_size = self.max_page_size
                elif page_size < 1:
                    page_size = self.page_size  # Fallback to default if invalid
            except ValueError:
                page_size = self.page_size  # Fallback to default if invalid
        else:
            page_size = self.page_size  # Default page size if not provided

        return page_size


class BookingReviewListPublicView(generics.ListAPIView):
    queryset = BookingReview.objects.all().order_by('-created_at')  # Latest reviews first
    serializer_class = BookingReviewSerializer
    permission_classes = [permissions.AllowAny]  # Adjust based on your security needs
    pagination_class = ReviewPagination

    def get_queryset(self):
        """
        Optionally filter reviews by property, host, or user.
        Query parameters:
        - `property_id`: ID of the property
        - `host_id`: ID of the host
        - `user_id`: ID of the reviewer
        - `page_size`: Number of reviews per page (mandatory)
        """
        queryset = super().get_queryset()

        # Retrieve query parameters
        property_id = self.request.query_params.get('property_id')
        host_id = self.request.query_params.get('host_id')
        user_id = self.request.query_params.get('user_id')
        page_size = self.request.query_params.get('page_size')
        req_user =  str(self.request.user.id)
        print(property_id, host_id, page_size, req_user)     
        # Ensure page_size is provided
        if not page_size:
            raise ValidationError({
                "error": "The 'page_size' query parameter is required."
            })

        # Apply filters
        if property_id:
            print('property_id', property_id)
            queryset = queryset.filter(property_id=property_id)
        if host_id and host_id==req_user:
            print('host_id', host_id)
            queryset = queryset.filter(host_id=host_id)
        if user_id and user_id==req_user: 
            print('user_id', user_id)    
            queryset = queryset.filter(user_id=user_id)

        return queryset

class BookingReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookingReview.objects.filter(user=self.request.user)
   

class HostReplyView(generics.UpdateAPIView):
    queryset = BookingReview.objects.all()
    serializer_class = BookingReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        review_id = kwargs.get('pk')
        reply_text = request.data.get('review_reply')
        print('reply_text', reply_text)
        print('review_id', review_id)

        try:
            # Fetch the review instance
            review = BookingReview.objects.get(id=review_id)

            # Ensure that the request user is the host of the review
            if review.host.id != request.user.id:
                print('You are not allowed to reply to this review.')
                raise PermissionDenied("You are not allowed to reply to this review.")

            # Update the review reply
            review.review_replay = reply_text
            review.save()
            print(review.review_replay)

            return Response({"success": "Reply saved successfully."}, status=200)
        except BookingReview.DoesNotExist:
            return Response({"error": "Review not found."}, status=404)
# ==========================RENT MANAGEMENT =========================================
class CreateRentView(APIView):
    def post(self, request, *args, **kwargs):
        print("Received data:", request.data)

        rent_details = request.data.get('rentDetails', {})
        rent_id = rent_details.get('id')
        rent_status = rent_details.get('status')
        booking_id = rent_details.get('booking_id')
        due_date = rent_details.get('due_date')
        amount = rent_details.get('amount')
        rent_method = rent_details.get('rent_method')
        notification_period = rent_details.get('notification_period', 3)  # Default to 3 if not provided

        if rent_id:
            rent_status = rent_status
        if not booking_id or not due_date or not amount or not rent_method:
            raise ValidationError({'error': 'booking_id, due_date, amount, and rent_method are required.'})

        try:
            booking = Bookings.objects.get(id=booking_id)
        except Bookings.DoesNotExist:
            raise NotFound({'error': 'Booking with the given ID does not exist.'})

        # Check for an existing rent with the same booking and due date
        rent, created = Rent.objects.update_or_create(
            booking=booking,
            status=rent_status,
            defaults={
                'due_date':due_date,
                'amount': amount,
                'rent_method': rent_method,
                'notification_period': notification_period,
            }
        )

        serializer = RentSerializer(rent)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        if booking.is_rent == False:
            booking.is_rent = True
            booking.save()
        return Response(serializer.data, status=status_code)

class GetUpcomingRentView(APIView):
    """
    Retrieve the upcoming rent for a specific booking ID with the earliest pending due date.
    """
    def get(self, request, booking_id):
        print('upcoming rent can be seen')
        # Validate booking
        try:
            booking = Bookings.objects.get(id=booking_id)
        except Bookings.DoesNotExist:
            return Response({"message": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the next rent with status 'pending' and the earliest due_date
        upcoming_rent = Rent.objects.filter(
            booking=booking,
            status__in=['pending', 'overdue'] 
            # due_date__gte=now().date()  # Ensure due_date is today or in the future
        ).order_by('due_date').first()

        today = now().date()
        if upcoming_rent.due_date < today:
            upcoming_rent.status = 'overdue'
            upcoming_rent.save()
        else:
            upcoming_rent.status = 'pending'
            upcoming_rent.save()
        if not upcoming_rent:
            return Response({"message": "No upcoming rent found for this booking."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the rent data
        rent_data = {
            "id": upcoming_rent.id,
            "host_email": upcoming_rent.booking.host.email ,
            "amount": float(upcoming_rent.amount),
            "due_date": upcoming_rent.due_date.strftime('%Y-%m-%d'),
            "notification_period": upcoming_rent.notification_period,
            "status": upcoming_rent.status,
            "rent_method": upcoming_rent.rent_method,
            "created_at": upcoming_rent.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": upcoming_rent.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        return Response({"upcoming_rent": rent_data}, status=status.HTTP_200_OK)


class PaidAndOverdueRentsView(APIView):
    def get(self, request, booking_id):
        try:
            rents = Rent.objects.filter(booking_id=booking_id, status__in=['paid', 'overdue'])
            if not rents.exists():
                return Response({'message': 'No rents found for the specified booking ID.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = RentSerializer(rents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Create_RentPayment(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print(request.body)
        rent_id = request.data.get('rent_id')
        rent = Rent.objects.get(id=rent_id)

        stripe.api_key = settings.STRIPE_SECRET_KEY  # Explicitly set the API key
        try:
            print(settings.STRIPE_SECRET_KEY, 'kkk')


            line_items = [{
                            'price_data': {
                                'currency': 'inr',
                                'unit_amount': int(rent.amount * 100),  # Convert to cents for Stripe
                                'product_data': {
                                    'name': 'HostHunt',
                                    'description': 'A booking for your stay at HostHunt',  # Provide a description
                                },
                            },
                            'quantity': 1,
                        }]

            print(line_items, 'lineee')
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                success_url=f"{BACKEND_BASE_URL}/booking/rent_payment_success/{rent.id}/",
                cancel_url=f"{BACKEND_BASE_URL}/payment-cancel/",
                metadata={'order_id': rent.id},
            )

            return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_403_FORBIDDEN)
        

class RentPaymentSuccess(APIView):
    permission_classes = []  # Adjust permissions as needed

    def save_current_rent_n_create_upcoming(self,pk):
        print('1')
        try:
            rent = Rent.objects.get(id=pk)

            # Mark rent as paid and record payment timestamp
            rent.status = 'paid'
            rent.payment_timestamp = now()
            rent.save()

            owner_id = rent.booking.host
            property = rent.booking.property
            user = rent.booking.user

            # Notify the property owner about the payment
            # Uncomment the following lines after integrating notifications
            # message = f"Your property '{property.property_name}' has received a rent payment from {user.name}."
            # async_to_sync(send_user_notification)(user_id=owner_id, message=message, type='rent', senderId=user)

            current_due_date = rent.due_date
            # Calculate the next month's first day as the due date
            next_month_due_date = (current_due_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            next_month_due_date = datetime.combine(next_month_due_date, datetime.min.time())  # Convert to datetime
            next_month_due_date = make_aware(next_month_due_date)  # Ensure timezone awareness

            # Create or update the next rent instance
            print('Creating/updating the upcoming rent')
            Rent.objects.update_or_create(
                booking=rent.booking,
                due_date=next_month_due_date,
                defaults={
                    'amount': rent.amount,
                    'rent_method': rent.rent_method,
                    'notification_period': rent.notification_period,
                    'status': 'pending',  # Default status for the new rent
                }
            )
            print('Created the upcoming rent')
            return rent.booking.id
        except Rent.DoesNotExist:
            print('11')
            return Response({'error': 'Rent not found'}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, pk):
        try:
            booking_id = self.save_current_rent_n_create_upcoming(pk)
            frontend_url = f"{FRONTEND_BASE_URL}/account/my-stays/{booking_id}/monthly-rent?paymentSuccess=true"        
            print('9',frontend_url)
            return HttpResponseRedirect(frontend_url)
        except Exception as e:
            print('10', e)
            return Response( status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, pk):
        try:
            booking_id = self.save_current_rent_n_create_upcoming(pk)
            if booking_id:
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print('10', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# ==========================================================================
# =======================  DASHBOARD====================================================
# ===========================================================================
from django.db.models import Count, Sum, Func
# from rest_framework.exceptions import ValidationError
from datetime import datetime

class TruncMonth(Func):
    function = "DATE_TRUNC"
    template = "%(function)s('month', %(expressions)s)"

class TruncWeek(Func):
    function = "DATE_TRUNC"
    template = "%(function)s('week', %(expressions)s)"


class BookingDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        frequency = request.GET.get("frequency", "monthly")  # Default to 'monthly'

        # Validate frequency
        if frequency not in ["monthly", "weekly"]:
            raise ValidationError({"error": "Invalid frequency parameter"})
        

        user = request.user
        print(user, 'user in dashboard datav')
        
        try:
            # Fetch data based on user type
            if user.is_staff:
                print('/////////////user is superuser///////////////////')
                bookings = Bookings.objects.all()
                rents = Rent.objects.all()
            else:
                print('///////////user is not superuser////////////////////')
                bookings = Bookings.objects.filter(host=user.id)
                rents = Rent.objects.filter(booking__host=user.id)

            # Determine the aggregation function based on frequency
            if frequency == "monthly":
                period_func = TruncMonth("check_in_date")
                period_rent_func = TruncMonth("booking__check_in_date")
            else:  # frequency == "weekly"
                period_func = TruncWeek("check_in_date")
                period_rent_func = TruncWeek("booking__check_in_date")

            # Aggregate bookings
            bookings_summary = (
                bookings.annotate(period=period_func)
                .values("period")
                .annotate(
                    booking_count=Count("id"),
                    total_revenue=Sum("booking_amount")  # Access related model field
                )
                .order_by("period")
            )

            # Aggregate rents
            rents_summary = (
                rents.annotate(period=period_rent_func)
                .values("period")
                .annotate(total_rent=Sum("amount"))
                .order_by("period")
            )

            # Format data for response
            summary_data = {
                datetime.strptime(str(entry["period"]).split(" ")[0], "%Y-%m-%d").strftime(
                    "%B %Y" if frequency == "monthly" else "Week of %d %B %Y"
                ): {
                    "booking_count": entry["booking_count"],
                    "total_revenue": entry["total_revenue"],
                }
                for entry in bookings_summary
            }

            rents_data = {
                datetime.strptime(str(entry["period"]).split(" ")[0], "%Y-%m-%d").strftime(
                    "%B %Y" if frequency == "monthly" else "Week of %d %B %Y"
                ): entry["total_rent"]
                for entry in rents_summary
            }

            # Prepare response
            data = {
                "bookings_summary": summary_data,
                "monthly_rents_details": rents_data,
            }

            return Response({"status": "success", "data": data})
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)


class DashboardSummaryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user,'user in dashboard summary')
        # Filter bookings and rents based on user's superuser status
        bookings_filter = {}
        rents_filter = {}
        properties_filter = {}

        print(user.is_staff)

        if not user.is_staff:
            bookings_filter['host'] = user.id
            rents_filter['booking__host'] = user.id
            properties_filter['host'] = user.id

        # Total Revenue (from Bookings and Monthly Rent)
        total_booking_revenue = Bookings.objects.filter(
            booking_status__in=['confirmed', 'checked_in', 'checked_out'],
            **bookings_filter
        ).aggregate(total=Sum('booking_amount'))['total'] or 0

        rent_revenue_notificationsOnly = Rent.objects.filter(
            status='paid',
            rent_method='notificationsOnly',
            **rents_filter
        ).aggregate(total=Sum('amount'))['total'] or 0

        rent_revenue_rentThroughHostHunt = Rent.objects.filter(
            status='paid',
            rent_method='rentThroughHostHunt',
            **rents_filter
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_rent_revenue = rent_revenue_notificationsOnly + rent_revenue_rentThroughHostHunt
        total_revenue = total_booking_revenue + total_rent_revenue

        # Total Bookings with specific statuses
        total_bookings = Bookings.objects.filter(
            booking_status__in=['checked_in', 'checked_out', 'confirmed'],
            **bookings_filter
        ).count()

        # Subscribed Bookings with specific statuses
        subscribed_bookings = Bookings.objects.filter(
            is_rent=True,
            booking_status__in=['checked_in', 'checked_out', 'confirmed'],
            **bookings_filter
        ).count()

        # Non-subscribed Bookings with specific statuses
        non_subscribed_bookings = total_bookings - subscribed_bookings

        # Bookings by Status
        checked_in_bookings = Bookings.objects.filter(
            booking_status='checked_in',
            **bookings_filter
        ).count()

        confirmed_bookings = Bookings.objects.filter(
            booking_status='confirmed',
            **bookings_filter
        ).count()

        checked_out_bookings = Bookings.objects.filter(
            booking_status='checked_out',
            **bookings_filter
        ).count()

        # Property counts
        total_properties = Property.objects.filter(**properties_filter).count()
        apartments_count = Property.objects.filter(property_type='apartment', **properties_filter).count()
        rentals_count = Property.objects.filter(property_type='rental', **properties_filter).count()
        pgs_count = Property.objects.filter(property_type='pg', **properties_filter).count()
        hostels_count = Property.objects.filter(property_type='hostel', **properties_filter).count()

        # Prepare Response
        data = {
            'total_revenue': total_revenue,
            'total_booking_revenue': total_booking_revenue,
            'total_rent_revenue': total_rent_revenue,
            'rent_revenue_notificationsOnly': rent_revenue_notificationsOnly,
            'rent_revenue_rentThroughHostHunt': rent_revenue_rentThroughHostHunt,
            'total_bookings': total_bookings,
            'subscribed_bookings': subscribed_bookings,
            'non_subscribed_bookings': non_subscribed_bookings,
            'checked_in_bookings': checked_in_bookings,
            'confirmed_bookings': confirmed_bookings,
            'checked_out_bookings': checked_out_bookings,
            'total_properties': total_properties,
            'apartments_count': apartments_count,
            'rentals_count': rentals_count,
            'pgs_count': pgs_count,
            'hostels_count': hostels_count,
        }

        return Response({"status": "success", "data": data})



class PaymentRecordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Extract query parameters
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        payment_type = request.query_params.get("payment_type", None)
        search_term = request.query_params.get("search", None)

        user = request.user
        
        # Filter rents based on parameters
        if user.is_staff:
            rents = Rent.objects.filter(status='paid')
            bookings = BookingPayment.objects.filter(status='paid')
            print(f'/////////////{user} is superuser prv///////////////////',rents,)

        else:
            rents = Rent.objects.filter(booking__host=user.id).filter(status='paid')
            print(f'///////////{user} is not superuser prv////////////////////',rents,)

        if start_date and end_date:
            rents = rents.filter(payment_timestamp__range=[start_date, end_date])

        if payment_type and payment_type != "all":
            rents = rents.filter(rent_method=payment_type)

        if search_term:
            rents = rents.filter(
                Q(booking__id__icontains=search_term) |
                Q(booking__guest_name__icontains=search_term)
            )

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(rents, request)

        # Serialize the data
        serializer = RentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

