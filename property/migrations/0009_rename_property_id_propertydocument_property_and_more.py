# Generated by Django 5.1.1 on 2024-10-21 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0008_rename_property_propertydocument_property_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='propertydocument',
            old_name='property_id',
            new_name='property',
        ),
        migrations.RenameField(
            model_name='propertyimage',
            old_name='property_id',
            new_name='property',
        ),
        migrations.RenameField(
            model_name='rentalapartment',
            old_name='property_id',
            new_name='property',
        ),
        migrations.RenameField(
            model_name='rooms',
            old_name='property_id',
            new_name='property',
        ),
    ]
