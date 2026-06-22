from rest_framework import serializers
from typing import Dict, Any
import re
from .models import (
    Skill, Company, Vacancy, Application, Resume, Review
)

class SkillSerializer(serializers.ModelSerializer):
    """Сериализатор для модели навыка"""
    class Meta:
        model = Skill
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    """Сериализатор для модели компании"""
    class Meta:
        model = Company
        fields = '__all__'

class VacancySerializer(serializers.ModelSerializer):
    """
    Сериализатор для вакансий.
    Реализованы вычисляемые поля и проверка на уникальность
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    skills_list = SkillSerializer(source='skills', many=True, read_only=True)

    # тут использую SerializerMethodField (см ниже)
    applications_count = serializers.SerializerMethodField()
    
    # передача данных через контекст (см ниже)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True}
        }

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проверяет, что правильно выставлены зп
        """
        # написала кастомную валидацию для поля зп
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "Зарплата 'от' не может быть больше зарплаты 'до'"
            )
        
        # проверка уникальности вакансии
        title = data.get('title')
        company = data.get('company') or getattr(self.instance, 'company', None)
        
        if title and company:
            qs = Vacancy.objects.filter(
                title=title, 
                company=company, 
                status__in=['published', 'draft']
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
                
            if qs.exists():
                raise serializers.ValidationError(
                    "У этой компании уже есть активная вакансия с таким названием"
                )
        
        return data
    
    def validate_contact_email(self, value: str) -> str:
        """Проверяет формат email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Некорректный формат email")
        return value

    def validate_contact_phone(self, value: str) -> str:
        """Проверяет формат телефона"""
        clean_value = re.sub(r'[\s\-\(\)]', '', value)
        pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(pattern, clean_value):
            raise serializers.ValidationError("Некорректный формат телефона")
        return value
    
    # реализация SerializerMethodField
    def get_applications_count(self, obj: Vacancy) -> int:
        """
        Возвращает количество откликов на вакансию.
        Использует аннотацию из queryset для оптимизации.
        
        Args:
            obj: Экземпляр вакансии
            
        Returns:
            int: Количество откликов
        """
        # если queryset был аннотирован во view, берем значение оттуда 
        if hasattr(obj, 'applications_count'):
            return obj.applications_count
        # фоллбэк, если аннотации нет
        return obj.applications.count()

    # реализация передачи данных через контекст
    def get_is_owner(self, obj: Vacancy) -> bool:
        """
        Проверяет, является ли текущий пользователь автором вакансии.
        Данные берутся из контекста запроса.
        
        Args:
            obj: Экземпляр вакансии
            
        Returns:
            bool: True если пользователь - автор
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.created_by == request.user
        return False
    
class ApplicationSerializer(serializers.ModelSerializer):
    candidate = serializers.PrimaryKeyRelatedField(read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    vacancy_title = serializers.CharField(source='vacancy.title', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    """Сериализатор для резюме соискателя"""
    skills_list = SkillSerializer(source='skills', many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}  # автор назначается автоматически
        }

    def validate_salary_expected(self, value: int) -> int:
        """Проверяет, что ожидаемая зарплата положительна"""
        if value and value <= 0:
            raise serializers.ValidationError("Зарплата должна быть больше нуля")
        return value

    def validate_experience_years(self, value: int) -> int:
        """Проверяет опыт работы"""
        if value > 50:
            raise serializers.ValidationError("Некорректное значение опыта")
        return value
    
class ReviewSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    vacancy_title = serializers.CharField(source='vacancy.title', read_only=True)
    company_name = serializers.CharField(source='vacancy.company.name', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'vacancy': {'read_only': True}  # Указываем вакансию через URL
        }

    def validate_rating(self, value: int) -> int:
        """Проверяет, что рейтинг от 1 до 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")
        return value