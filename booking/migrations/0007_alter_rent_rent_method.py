# Generated by Django 5.1.1 on 2024-12-16 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0006_alter_rent_rent_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rent',
            name='rent_method',
            field=models.CharField(choices=[('notificationsOnly', 'Notification Only'), ('rentThroughHostHunt', 'Rent Through HostHunt')], default='notificationsOnly', max_length=20),
        ),
    ]
