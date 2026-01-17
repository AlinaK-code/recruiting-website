# менеджмент комманда, для назначения собесов
# использовать: docker-compose exec web python manage.py notify_interviews
# чтобы проверить все комманды использовала docker-compose exec web python manage.py help
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import Interview

class Command(BaseCommand):
    help = 'Показывает предстоящие собеседования на сегодня'

    def handle(self, *args, **options):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        interviews = Interview.objects.filter(
            scheduled_at__date=today,
            status='scheduled'
        )

        if interviews:
            self.stdout.write(self.style.SUCCESS(f'Найдено {interviews.count()} собеседований на сегодня:'))
            for interview in interviews:
                self.stdout.write(f'- {interview}')
        else:
            self.stdout.write('Собеседований на сегодня нет.')