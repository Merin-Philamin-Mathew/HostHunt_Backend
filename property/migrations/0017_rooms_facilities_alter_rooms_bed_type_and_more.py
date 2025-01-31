# Generated by Django 5.1.1 on 2024-11-05 05:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0016_bedtype_roomfacilities_roomtype_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rooms',
            name='facilities',
            field=models.ManyToManyField(related_name='rooms', to='property.roomfacilities'),
        ),
        migrations.AlterField(
            model_name='rooms',
            name='bed_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='property.bedtype'),
        ),
        migrations.AlterField(
            model_name='rooms',
            name='room_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room', to='property.roomtype'),
        ),
    ]
