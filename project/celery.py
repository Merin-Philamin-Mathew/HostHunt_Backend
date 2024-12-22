from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Create the Celery app
app = Celery('project')

# Load task-related settings from the Django settings file with a 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in all installed apps
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'send-rent-notifications': {
#         'task': 'booking.tasks.send_rent_notifications',
#         'schedule': crontab(hour=13, minute=51),  # Run daily at 9 AM
#     },
# }

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
