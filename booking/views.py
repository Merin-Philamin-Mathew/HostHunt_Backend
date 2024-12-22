from django.conf import settings

from datetime import datetime
from rest_framework import permissions,status,generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

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



class CreatePayment(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        print(booking,booking_payment,'fslkfslk')
        stripe.api_key = settings.STRIPE_SECRET_KEY  # Explicitly set the API key
        try:
            print(settings.STRIPE_SECRET_KEY, 'kkk')


            image_url = image_url
            line_items = [{
                            'price_data': {
                                'currency': 'inr',
                                'unit_amount': int(booking_amount * 100),  # Convert to cents for Stripe
                                'product_data': {
                                    'name': 'HostHunt',
                                    'description': 'A booking for your stay at HostHunt',  # Provide a description
                                    'images': [image_url],  # Optional, but useful for the product display
                                },
                            },
                            'quantity': 1,
                        }]

            print(line_items, 'lineee')
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                success_url=f"http://localhost:8000/booking/payment-success/{booking.id}/",
                cancel_url=f"http://localhost:8000/payment-cancel/",
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

            booking.booking_status = 'confirmed'
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
            print('going to sent notification to othe property ownere')
            async_to_sync(send_user_notification)(user_id=owner_id, message=message, type='booking', senderId=booking.user.id)

            print('notification sent from the payment success view')

            frontend_url = f"http://localhost:5173/account/my-stays?booking_id={pk}"
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
         

class HostBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensures the user is authenticated

    def get(self, request):
        user = request.user
        print(user)
        bookings = Bookings.objects.filter(host=user).order_by('-id').select_related('property', 'room')
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

    def patch(self, request, booking_id):
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
        bookings = Bookings.objects.filter(user=user).order_by('-id').select_related('property', 'room')
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

class BookingReviewListCreateView(generics.ListCreateAPIView):
 
    serializer_class = BookingReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookingReview.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

class BookingReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookingReview.objects.filter(user=self.request.user)
   
# ==========================RENT MANAGEMENT =========================================
class CreateRentView(APIView):
    def post(self, request, *args, **kwargs):
        print("Received data:", request.data)

        rent_details = request.data.get('rentDetails', {})
        booking_id = rent_details.get('booking_id')
        due_date = rent_details.get('due_date')
        amount = rent_details.get('amount')
        rent_method = rent_details.get('rent_method')
        notification_period = rent_details.get('notification_period', 3)  # Default to 3 if not provided

        if not booking_id or not due_date or not amount or not rent_method:
            raise ValidationError({'error': 'booking_id, due_date, amount, and rent_method are required.'})

        try:
            booking = Bookings.objects.get(id=booking_id)
        except Bookings.DoesNotExist:
            raise NotFound({'error': 'Booking with the given ID does not exist.'})

        # Check for an existing rent with the same booking and due date
        rent, created = Rent.objects.update_or_create(
            booking=booking,
            status='pending',
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
        print('upcoming rent can be seem')
        # Validate booking
        try:
            booking = Bookings.objects.get(id=booking_id)
        except Bookings.DoesNotExist:
            return Response({"message": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch the next rent with status 'pending' and the earliest due_date
        upcoming_rent = Rent.objects.filter(
            booking=booking,
            status='pending',
            due_date__gte=now().date()  # Ensure due_date is today or in the future
        ).order_by('due_date').first()

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
            print(rents)
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
        rent_id = int(request.data.get('rent_id'))
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
                success_url=f"http://localhost:8000/booking/rent_payment_success/{rent.id}/",
                cancel_url=f"http://localhost:8000/payment-cancel/",
                metadata={'order_id': rent.id},
            )

            return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_403_FORBIDDEN)
        

class RentPaymentSuccess(APIView):
    permission_classes = []

    def get(self, request, pk):
        try:
            print('1')
            rent = Rent.objects.get(id=pk)

            rent.status = 'paid'
            rent.save()

            owner_id = rent.booking.host
            property = rent.booking.property
            user = rent.booking.user

            # message = f"Your property '{property.property_name}' has received a rent payment from {user.name}."
            print('8')
            # print('going to sent notification to othe property ownere')
            # async_to_sync(send_user_notification)(user_id=owner_id, message=message, type='rent', senderId=user)

            # print('notification sent from the payment success view')

            current_due_date = rent.due_date
            # Calculate the next month's first day as the due date

            next_month_due_date = (current_due_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            next_month_due_date = datetime.combine(next_month_due_date, datetime.min.time())  # Convert to datetime
            next_month_due_date = make_aware(next_month_due_date)  # Ensure timezone awareness if needed

            # Create the next rent instance if it doesn't already exist
            print('going to create an upcoming rent')
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

            print('created the upcoming rent')
            frontend_url = f"http://localhost:5173/account/my-stays/{rent.booking.id}/monthly-rent?paymentSuccess=true"
            
            print('9')
            return HttpResponseRedirect(frontend_url)
        
        except Rent.DoesNotExist:
            print('11')
            return Response({'error': 'Booking not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('10',e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



