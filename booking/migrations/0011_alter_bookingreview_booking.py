# Generated by Django 5.1.1 on 2024-12-19 12:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0010_alter_bookingreview_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingreview',
            name='booking',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='booking.bookings'),
        ),
    ]