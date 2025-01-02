from django.db import migrations, models
from django.utils.timezone import now
import uuid

def populate_new_id(apps, schema_editor):
    Bookings = apps.get_model('booking', 'Bookings')
    for booking in Bookings.objects.all():
        if not booking.new_id:  # Populate only if new_id is not already set
            today = now().strftime('%Y%m%d')  # Format YYYYMMDD
            unique_number = str(uuid.uuid4().int)[:4]
            booking.new_id = f"BK{today}{unique_number}"
            booking.save()

class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_alter_bookingreview_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookings',
            name='new_id',
            field=models.CharField(max_length=20, unique=True, blank=True, null=True),
        ),
        migrations.RunPython(populate_new_id),
        migrations.AlterField(
            model_name='bookings',
            name='new_id',
            field=models.CharField(max_length=20, unique=True, blank=False, null=False),
        ),
    ]
