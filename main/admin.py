from django.contrib import admin
from django.utils.html import format_html # помогает безопасно вставлять html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

# импортирую все модели
from .models import (
    Skill, Company, CandidateProfile, RecruiterProfile,
    Vacancy, Application, Interview, Feedback, Resume, Review
)

# таблица-справочник навыков
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['id','name'] # то, какие столбцы показывать
    search_fields = ['name'] 
    ordering = ['name']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city', 'logo_preview', 'created_at']
    list_filter = ['city', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['name', 'description', 'logo', 'city', 'created_at', 'updated_at']

    @admin.display(description="Логотип")
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.logo.url)
        return "-"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Администратор видит ВСЕ компании
        if request.user.is_staff:
            return qs
            
        # Рекрутер видит ТОЛЬКО свою компанию
        if hasattr(request.user, 'recruiter_profile') and request.user.recruiter_profile:
            recruiter_company = request.user.recruiter_profile.company
            return qs.filter(pk=recruiter_company.pk)
            
        # Обычный пользователь не видит ничего
        return qs.none()

    def save_model(self, request, obj, form, change):
        # Если это не админ, проверяем права рекрутера
        if not request.user.is_staff:
            if hasattr(request.user, 'recruiter_profile') and request.user.recruiter_profile:
                # Запрещаем редактировать чужую компанию или создавать новую
                if obj.pk and obj.pk != request.user.recruiter_profile.company.pk:
                    from django.core.exceptions import PermissionDenied
                    raise PermissionDenied("Вы можете редактировать только свою компанию.")
            else:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("У вас нет прав для управления компаниями.")
                
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        """Создание новых компаний доступно ТОЛЬКО администраторам"""
        return request.user.is_staff


# профили
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['id','full_name', 'user_email', 'avatar_preview', 'created_at']
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
    list_display = ['id','contact_person', 'company_name', 'user_email', 'created_at']
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

# для экспорта в эксель 
class VacancyResource(resources.ModelResource):
    company_name = Field(attribute='company__name', column_name='Компания')
    salary_range = Field(column_name='Зарплата')

    class Meta:
        model = Vacancy
        fields = ('id', 'title', 'company_name', 'salary_min', 'salary_max', 'status', 'created_at', 'salary_range')
        export_order = ('id', 'title', 'company_name', 'salary_range', 'status', 'created_at')

    # исп метод dehydrate_{field_name}
    def dehydrate_salary_range(self, vacancy):
        if vacancy.salary_min and vacancy.salary_max:
            return f"{vacancy.salary_min} – {vacancy.salary_max}"
        elif vacancy.salary_min:
            return f"от {vacancy.salary_min}"
        elif vacancy.salary_max:
            return f"до {vacancy.salary_max}"
        return "не указана"

    # использовала метод get_{field_name}
    def get_recruiter_email(self, vacancy):
        return vacancy.created_by.email if vacancy.created_by else "Не указан"
    
    # использовала метод get_export_queryset
    def get_export_queryset(self):
        # экспортирую только опубликованные вакансии!!!
        return Vacancy.objects.filter(status='published')
    
    
@admin.register(Vacancy)
class VacancyAdmin(ImportExportModelAdmin):
    resource_class = VacancyResource
    list_display = ['id','title', 'company_name', 'salary_range', 'status', 'created_by_email', 'created_at']
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
    list_display = ['id','candidate_email', 'vacancy_title', 'status', 'applied_at']
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
    list_display = ['id','application_info', 'scheduled_at', 'format', 'status']
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
    list_display = ['id','interview_info', 'rating', 'created_by_email', 'created_at']
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
    

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'salary_expected', 'experience_years', 'updated_at']
    list_filter = ['experience_years', 'updated_at']
    search_fields = ['title', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['skills']  # Удобный виджет для ManyToMany
    raw_id_fields = ['user']        # Чтобы не грузить список всех пользователей при выборе


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'vacancy_title', 'rating_stars', 'text_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['text', 'user__username', 'vacancy__title']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'vacancy']

    @admin.display(description="Вакансия")
    def vacancy_title(self, obj):
        return obj.vacancy.title

    @admin.display(description="Оценка")
    def rating_stars(self, obj):
        """Отображение к-ва звезд"""
        return "⭐" * obj.rating

    @admin.display(description="Текст отзыва")
    def text_preview(self, obj):
        """Показывает только начало текста, чтобы не растягивать таблицу."""
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text