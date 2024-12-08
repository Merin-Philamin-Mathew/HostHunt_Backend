from django.conf import settings

from datetime import datetime
from rest_framework import permissions,status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import HttpResponseRedirect
import os, stripe
from .models import Bookings, BookingPayment
from property.models import Rooms, Property
from .serializer import BookingSerializer

from django.http import JsonResponse
from web_sockets.utils import send_user_notification
from asgiref.sync import async_to_sync



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
                # success_url=f"http://localhost:8000/payment-success/{order.id}/",
                cancel_url=f"http://localhost:8000/payment-cancel/",
                metadata={'order_id': booking.id},
                # metadata={'order_id': order_id},
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
            print('going to sent notification to othe property ownere')
            async_to_sync(send_user_notification)(user_id=owner_id, message=message, type='booking', senderId=booking.user.id)

            print('notification sent from the payment success view')

            frontend_url = f"http://localhost:5173/manage-account/my-stays?booking_id={pk}"
            return HttpResponseRedirect(frontend_url)
        
        except Bookings.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class BookingDetailsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, booking_id):
#         try:
#             # Fetch the booking based on the ID
#             booking = Bookings.objects.get(id=booking_id)
            
#             # Check if the user is authorized to view the booking
#             if booking.user != request.user and booking.host != request.user:
#                 return Response(
#                     {"error": "You do not have permission to view this booking."},
#                     status=status.HTTP_403_FORBIDDEN
#                 )

#             # Serialize the booking data
#             serializer = BookingSerializer(booking)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Bookings.DoesNotExist:
#             return Response(
#                 {"error": "Booking not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# =========================USER MANAGEMENT================================
class UserBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensures the user is authenticated

    def get(self, request):
        user = request.user
        print(user)
        bookings = Bookings.objects.filter(user=user).select_related('property', 'room')
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
    

class UserBookingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensures the user is authenticated

    def get(self, request):
        user = request.user
        print(user)
        bookings = Bookings.objects.filter(user=user).select_related('property', 'room')
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
    




    