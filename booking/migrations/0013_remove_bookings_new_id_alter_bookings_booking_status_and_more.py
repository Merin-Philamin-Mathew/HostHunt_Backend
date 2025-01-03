# Generated by Django 5.1.1 on 2024-12-28 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_auto_20241228_1657'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookings',
            name='new_id',
        ),
        migrations.AlterField(
            model_name='bookings',
            name='booking_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('reserved', 'Reserved'), ('confirmed', 'Confirmed'), ('checked_in', 'Checked_In'), ('checked_out', 'Checked_Out'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='bookings',
            name='id',
            field=models.CharField(blank=True, editable=False, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
    ]