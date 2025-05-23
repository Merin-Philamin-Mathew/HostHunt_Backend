# Generated by Django 5.1.1 on 2025-01-24 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_rename_is_active_user_customuser_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identityverification',
            name='identity_card',
            field=models.CharField(blank=True, choices=[('passport', 'Passport'), ('pan', 'PAN Card'), ('driving_license', 'Driving License'), ('voter_id', 'Voter ID'), ('social_security', 'Social Security Card'), ('national_id', 'National ID'), ('residence_permit', 'Residence Permit'), ('identity_card', 'Identity Card')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='identityverification',
            name='identity_proof_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
