# Generated by Django 5.1.1 on 2024-09-23 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_customuser_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='name',
            field=models.CharField(),
        ),
    ]