# Generated by Django 5.1.1 on 2024-12-04 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0026_rename_occupancy_rooms_no_of_beds_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rooms',
            name='booking_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='rooms',
            name='booking_amount_choice',
            field=models.CharField(choices=[('price_per_night', 'Price per night'), ('monthly_rent', 'Monthly Rent')], default='monthly_rent', max_length=20),
        ),
    ]
