from django.shortcuts import render

from django.conf import settings



from datetime import datetime
from rest_framework import permissions,status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import HttpResponseRedirect
import os, stripe
from .models import Bookings, BookingPayment
from property.models import Rooms, Property


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
            host=room.property.host,  # Assuming the host is linked to the property
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
                success_url=f"http://localhost:8000/property/payment-success/{booking.id}/",
                # success_url=f"http://localhost:8000/payment-success/{order.id}/",
                cancel_url=f"http://localhost:8000/payment-cancel/",
                metadata={'order_id': 10},
                # metadata={'order_id': order_id},
            )

            return Response({'id': checkout_session.id}, status=status.HTTP_200_OK)
        # except Orders.DoesNotExist:
        #     return Response({'error': 'Order not found.'}, status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status.HTTP_403_FORBIDDEN)
        

class PaymentSuccess(APIView):
    permission_classes = []

    def get(self, request, pk):
        try:
            booking = Bookings.objects.get(id=pk)
            booking_payment = BookingPayment.objects.get(Booking=booking)

            # You can update the payment status here if needed
            booking_payment.status = 'paid'
            booking_payment.save()

            frontend_url = f"http://localhost:5173/trial-page/"
            return HttpResponseRedirect(frontend_url)
        
        except Bookings.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

