from rest_framework import serializers
from .models import (
    Skill, Company, Vacancy
)

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class VacancySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    skills_list = SkillSerializer(source='skills', many=True, read_only=True)

    class Meta:
        model = Vacancy
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True}
        }

    def validate(self, data):
        """Кастомная валидация: зарплата от не может быть больше зарплаты до"""
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError(
                "Зарплата 'от' не может быть больше зарплаты 'до'"
            )
        return data