# Generated by Django 5.1.1 on 2024-11-21 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0020_rooms_room_thumbnail_image_url_alter_property_lat_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rooms',
            name='room_thumbnail_image_url',
            field=models.URLField(max_length=255),
        ),
    ]
