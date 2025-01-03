# Generated by Django 5.1.1 on 2024-12-13 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_bookings_is_rent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent',
            name='rent_method',
            field=models.CharField(choices=[('notificationsOnly', 'Notification Only'), ('rentThroughHostHunt', 'Rent Through HostHunt')], default='notification', max_length=20),
        ),
    ]