# Generated by Django 5.1.1 on 2024-12-10 06:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingpayment',
            name='Booking',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='booking_payment', to='booking.bookings'),
        ),
        migrations.AlterField(
            model_name='bookings',
            name='booking_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('reserved', 'Reserved'), ('confirmed', 'Confirmed'), ('checked_in', 'Cheched_In'), ('checked_out', 'Checked_Out'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
    ]