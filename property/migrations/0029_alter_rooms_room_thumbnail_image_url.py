# Generated by Django 5.1.1 on 2024-12-04 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0028_alter_rooms_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rooms',
            name='room_thumbnail_image_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]