from django.contrib import admin
from django.utils.html import format_html # помогает безопасно вставлять html

# импортирую все модели
from .models import (
    Skill, Company, CandidateProfile, RecruiterProfile,
    Vacancy, Application, Interview, Feedback
)

# таблица-справочник навыков
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name'] # то, какие столбцы показывать
    search_fields = ['name'] 
    ordering = ['name']


# компании
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'logo_preview', 'created_at'] # logo_preview - ф-ия возвр изображение
    list_filter = ['city', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['name', 'description', 'logo', 'city', 'created_at', 'updated_at']

    @admin.display(description="Логотип") # создаю кастомные столбцы для того, чтобы можно было видеть фото
    def logo_preview(self, obj):
        if obj.logo: #если нет фото
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.logo.url)
        return "-"


# профили
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user_email', 'avatar_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['full_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['skills'] #для легкого выбора ManyToMany (навыки).
    raw_id_fields = ['user']

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Аватар")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.avatar.url)
        return "-"


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['contact_person', 'company_name', 'user_email', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['contact_person', 'user__email', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'company']

    @admin.display(description="Компания")
    def company_name(self, obj):
        return obj.company.name

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email


# вакансии
class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    fields = ['candidate', 'status', 'applied_at']
    readonly_fields = ['applied_at']
    raw_id_fields = ['candidate']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'salary_range', 'status', 'created_by_email', 'created_at']
    list_filter = ['status', 'company', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['skills']
    raw_id_fields = ['company', 'created_by']
    inlines = [ApplicationInline]

    @admin.display(description="Компания")
    def company_name(self, obj):
        return obj.company.name

    @admin.display(description="Зарплата")
    def salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            return f"{obj.salary_min} – {obj.salary_max}"
        elif obj.salary_min:
            return f"от {obj.salary_min}"
        elif obj.salary_max:
            return f"до {obj.salary_max}"
        return "не указана"

    @admin.display(description="Автор")
    def created_by_email(self, obj):
        return obj.created_by.email


# отклики
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate_email', 'vacancy_title', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['candidate__email', 'vacancy__title']
    date_hierarchy = 'applied_at'
    readonly_fields = ['applied_at', 'reviewed_at']
    raw_id_fields = ['candidate', 'vacancy']

    @admin.display(description="Кандидат")
    def candidate_email(self, obj):
        return obj.candidate.email

    @admin.display(description="Вакансия")
    def vacancy_title(self, obj):
        return obj.vacancy.title


# собеседования
@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['application_info', 'scheduled_at', 'format', 'status']
    list_filter = ['format', 'status', 'scheduled_at']
    date_hierarchy = 'scheduled_at'
    readonly_fields = ['created_at']
    raw_id_fields = ['application']

    @admin.display(description="Отклик")
    def application_info(self, obj):
        return f"{obj.application.candidate.email} → {obj.application.vacancy.title}"


# обратная связь
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['interview_info', 'rating', 'created_by_email', 'created_at']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['interview', 'created_by']

    @admin.display(description="Собеседование")
    def interview_info(self, obj):
        app = obj.interview.application
        return f"{app.candidate.email} → {app.vacancy.title}"

    @admin.display(description="Автор")
    def created_by_email(self, obj):
        return obj.created_by.email