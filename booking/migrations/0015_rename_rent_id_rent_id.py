# Generated by Django 5.1.1 on 2024-12-28 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0014_remove_rent_id_rent_rent_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rent',
            old_name='rent_id',
            new_name='id',
        ),
    ]
