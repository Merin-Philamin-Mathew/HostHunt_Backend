# Generated by Django 5.1.1 on 2024-09-20 15:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_owner',
        ),
    ]