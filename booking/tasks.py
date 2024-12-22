# rent/tasks.py
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Rent


from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

@shared_task
def send_rent_notifications():
    print('=================================')
    current_date = timezone.now().date()
    upcoming_rents = Rent.objects.filter(
        due_date__range=[current_date, current_date + timezone.timedelta(days=3)],
        status='pending'
    )
    print(f'Found {upcoming_rents.count()} upcoming rents')

    for rent in upcoming_rents:
        try:
            user_name = rent.booking.user.name
            email_context = {
                'user_name': user_name,
                'amount': rent.amount,
                'due_date': rent.due_date,
            }

            if rent.rent_method == 'rentThroughHostHunt':
                print('rentThroughHostHunt')
                email_context['payment_url'] = f"http://localhost:5173/account/my-stays/{rent.booking.id}/monthly-rent" 
                print('rentThroughHostHunt')
                html_template = 'emails/rent_through_hosthunt.html'
            else:
                print('notificationsOnly')
                html_template = 'emails/rent_notification_only.html'
            
            print(html_template)

            # Render the chosen template
            html_content = render_to_string(html_template, email_context)
            text_content = strip_tags(html_content)

            # Send email
            email = EmailMultiAlternatives(
                subject="Upcoming Rent Payment Reminder",
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[rent.booking.user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        except Exception as e:
            print(f"Error sending email to {rent.booking.user.email}: {e}")
