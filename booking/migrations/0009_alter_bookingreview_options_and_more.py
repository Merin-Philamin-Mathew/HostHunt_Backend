# Generated by Django 5.1.1 on 2024-12-19 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_bookingreview_reviewlikedislike'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookingreview',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='bookingreview',
            unique_together=set(),
        ),
    ]
