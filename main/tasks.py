from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Vacancy

@shared_task
def cleanup_old_drafts():
    """Удаляет черновики старше 30 дней"""
    threshold = timezone.now() - timedelta(days=30)
    deleted_count, _ = Vacancy.objects.filter(
        status='draft', 
        created_at__lt=threshold
    ).delete()
    return f"Удалено {deleted_count} старых черновиков"