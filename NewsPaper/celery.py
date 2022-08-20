import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace = 'CELERY')

app.autodiscover_tasks()


from celery.schedules import crontab

app.conf.beat_schedule = {
    'action_every_monday_0am': {
        'task': 'news.tasks.notify_subscribers_weekly',
        # 'schedule': crontab(), # Uncomment to test this feature
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}