import time

from datetime import timedelta
from pprint import pformat

from django.db.models import F, OuterRef, Subquery
from django.utils import timezone

from huey import crontab
from huey.contrib.djhuey import db_task, db_periodic_task, HUEY
from huey.exceptions import TaskLockedException

from camp.apps.monitors.models import Entry
from camp.apps.monitors.purpleair import api
from camp.apps.monitors.purpleair.models import PurpleAir


@db_periodic_task(crontab(minute='*'), priority=50)
def import_recent_data():
    print('[import_recent_data]')
    for monitor in PurpleAir.objects.all():
        print('\n' * 10, '[import_recent_data]', monitor.name, '\n' * 10)
        import_monitor_data.schedule([monitor.pk], delay=1, priority=30)


@db_task()
def import_monitor_history(monitor_id, end=None):
    monitor = PurpleAir.objects.get(pk=monitor_id)
    end = end or timezone.now()
    feed = list(monitor.feed(end=end, results=8000))

    if len(feed):
        print(f'[history] {monitor.name} ({monitor.pk}) | {end} | {len(feed)}')
        for items in feed:
            add_monitor_entry(monitor.pk, items)
        end = min([min([i['created_at'] for i in items]) for items in feed]) - timedelta(seconds=1)
        import_monitor_history(monitor_id, end)


@db_task()
def import_monitor_data(monitor_id, options=None):
    monitor = PurpleAir.objects.get(pk=monitor_id)
    print(f'[import_monitor_data:start] {monitor.name} ({monitor.pk})')
    monitor.update_info()
    monitor.save()

    if options is None:
        try:
            options = {'start': monitor.entries.latest('timestamp').timestamp}
        except Entry.DoesNotExist:
            options = {'results': 1}

    feed = monitor.feed(**options)
    for index, payload in enumerate(feed):
        add_monitor_entry.schedule([monitor.pk, payload], delay=1, priority=10)

    print(f'[import_monitor_data:end] {monitor.name} ({monitor.pk}) - {index + 1}')


@db_task()
def add_monitor_entry(monitor_id, payload):
    key = f'purpleair_entry_{monitor_id}_{payload[0]["created_at"]}'
    try:
        with HUEY.lock_task(key):
            monitor = PurpleAir.objects.select_related('latest').get(pk=monitor_id)
            print(f'[add_monitor_entry] {monitor.name} ({monitor.pk})')
            entry = monitor.create_entry(payload)
            entry = monitor.process_entry(entry)
            entry.save()

            if monitor.latest is None or (entry.timestamp > monitor.latest.timestamp):
                monitor.latest = entry
                monitor.save()
    except TaskLockedException:
        print(f'[LOCKED:add_monitor_entry] {monitor_id} ({payload[0]["created_at"]})')