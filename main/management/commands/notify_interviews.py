# main/management/commands/notify_interviews.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone
from main.models import Interview

class Command(BaseCommand):
    help = 'Показывает предстоящие собеседования на сегодня (по локальному времени)'

    def handle(self, *args, **options):
        # Текущее время в локальном часовом поясе (Europe/Moscow)
        now_local = timezone.localtime(timezone.now())
        today = now_local.date()

        # Начало и конец дня в локальном времени
        start_local = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_local = timezone.make_aware(datetime.combine(today, datetime.max.time()))

        # Переводим в UTC с помощью datetime.timezone.utc
        start_utc = start_local.astimezone(dt_timezone.utc)
        end_utc = end_local.astimezone(dt_timezone.utc)

        interviews = Interview.objects.filter(
            scheduled_at__gte=start_utc,
            scheduled_at__lte=end_utc,
            status='scheduled'
        )

        if interviews.exists():
            self.stdout.write(self.style.SUCCESS(f'Найдено {interviews.count()} собеседований на сегодня ({today}):'))
            for interview in interviews:
                local_time = timezone.localtime(interview.scheduled_at)
                self.stdout.write(
                    f'- {interview.application.candidate.email} → '
                    f'{interview.application.vacancy.title} | '
                    f'{local_time.strftime("%H:%M")} ({interview.get_format_display()})'
                )
        else:
            self.stdout.write(f'Собеседований на сегодня ({today}) нет.')