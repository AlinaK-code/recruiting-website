from rest_framework import serializers
from typing import Dict, Any
from .models import (
    Skill, Company, Vacancy, Application
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
        
        Args:
            data: Словарь валидированных данных
            
        Returns:
            Dict[str, Any]: Проверенные данные
            
        Raises:
            serializers.ValidationError: Если min > max
        """
        # написала кастомную валидацию для поля зп
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "Зарплата 'от' не может быть больше зарплаты 'до'"
            )
        return data
    
    
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
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    vacancy_title = serializers.CharField(source='vacancy.title', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'