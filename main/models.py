from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

# навыки
class Skill(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название"
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ['name']

    def __str__(self):
        return self.name
  
# компания  
class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    logo = models.ImageField(
        upload_to='companies/logos/',
        blank=True,
        null=True,
        verbose_name="Логотип"
    )
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ['name']

    def __str__(self):
        return self.name
 
# профиль кандидата   
class CandidateProfile(models.Model):
    user = models.OneToOneField( #OneToOneField - 1 пользователь = 1 профиль
        User,
        on_delete=models.CASCADE,
        related_name='candidate_profile',
        verbose_name="Пользователь"
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(
        upload_to='candidates/avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    portfolio_url = models.URLField(blank=True, verbose_name="Портфолио")
    skills = models.ManyToManyField( # 1 пользователь может иметь много навыков
        Skill,
        blank=True,
        verbose_name="Навыки"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Профиль кандидата"
        verbose_name_plural = "Профили кандидатов"

    def __str__(self):
        return f"{self.full_name} ({self.user.email})"


# профиль рекрутера
class RecruiterProfile(models.Model):
    user = models.OneToOneField( #OneToOneField - 1 пользователь = 1 профиль
        User,
        on_delete=models.CASCADE,
        related_name='recruiter_profile',
        verbose_name="Пользователь"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Компания"
    )
    contact_person = models.CharField(max_length=255, verbose_name="Контактное лицо")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Профиль рекрутера"
        verbose_name_plural = "Профили рекрутеров"

    def __str__(self):
        return f"{self.contact_person} ({self.company.name})"
    
    
# вакансия 
class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликована'),
        ('closed', 'Закрыта'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    salary_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Зарплата от"
    )
    salary_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Зарплата до"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Статус"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Компания"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Создал"
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        verbose_name="Требуемые навыки"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")
    
    # история изменений, автоматически создаст таблицу main_historicalvacancy где будут хоаниться изменения
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    
# заявка на работу 
class Application(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Подана'),
        ('reviewed', 'Рассмотрена'),
        ('interview_scheduled', 'Собеседование назначено'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонёна'),
    ]

    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Кандидат"
    )
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Вакансия"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted',
        verbose_name="Статус"
    )
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отклика")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата рассмотрения")

    class Meta:
        verbose_name = "Отклик"
        verbose_name_plural = "Отклики"
        unique_together = ('candidate', 'vacancy')  # один кандидат — один отклик на вакансию

    def __str__(self):
        return f"{self.candidate.email} → {self.vacancy.title}"
    

# собеседование 
class Interview(models.Model):
    FORMAT_CHOICES = [
        ('online', 'Онлайн'),
        ('offline', 'Офлайн'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Назначено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        verbose_name="Отклик"
    )
    scheduled_at = models.DateTimeField(verbose_name="Дата и время")
    duration_minutes = models.PositiveSmallIntegerField(
        default=60,
        verbose_name="Длительность (минут)"
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='online',
        verbose_name="Формат"
    )
    meeting_link = models.URLField(blank=True, verbose_name="Ссылка на встречу")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Собеседование"
        verbose_name_plural = "Собеседования"
        ordering = ['scheduled_at']

    def __str__(self):
        return f"Интервью для {self.application.candidate.email} ({self.scheduled_at.strftime('%d.%m.%Y %H:%M')})"
    
    
# обратная связь 
class Feedback(models.Model):
    interview = models.OneToOneField(
        Interview,
        on_delete=models.CASCADE,
        verbose_name="Собеседование"
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Оценка (1-5)"
    )
    comments = models.TextField(blank=True, verbose_name="Комментарии")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"

    def __str__(self):
        return f"Фидбэк от {self.created_by.email} для {self.interview.application.candidate.email}"
    