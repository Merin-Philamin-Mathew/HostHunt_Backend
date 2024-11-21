# Generated by Django 5.1.1 on 2024-11-08 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0018_property_lat_property_lng_property_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='lat',
            field=models.DecimalField(decimal_places=20, max_digits=25),
        ),
        migrations.AlterField(
            model_name='property',
            name='lng',
            field=models.DecimalField(decimal_places=20, max_digits=25),
        ),
        migrations.AlterField(
            model_name='property',
            name='location',
            field=models.CharField(max_length=255),
        ),
    ]
