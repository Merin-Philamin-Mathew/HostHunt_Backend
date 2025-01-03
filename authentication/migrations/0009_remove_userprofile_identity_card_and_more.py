# Generated by Django 5.1.1 on 2024-12-16 14:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_rename_is_active_customuser_is_active_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='identity_card',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='identity_proof_number',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_pic',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.CreateModel(
            name='IdentityVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identity_card', models.CharField(blank=True, max_length=50, null=True)),
                ('identity_proof_number', models.CharField(blank=True, choices=[('passport', 'Passport'), ('pan', 'PAN Card'), ('driving_license', 'Driving License'), ('voter_id', 'Voter ID'), ('social_security', 'Social Security Card'), ('national_id', 'National ID'), ('residence_permit', 'Residence Permit'), ('identity_card', 'Identity Card')], max_length=100, null=True)),
                ('identity_card_front_img_url', models.URLField(max_length=500)),
                ('identity_card_back_img_url', models.URLField(max_length=500)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
