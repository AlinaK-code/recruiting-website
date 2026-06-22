# main/forms.py
from django import forms
from .models import Vacancy, Company

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        exclude = ['created_by', 'status']
        widgets = {
            'skills': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            
            # ДОБАВЛЕНЫ КОНТАКТНЫЕ ПОЛЯ:
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'hr@company.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 000-00-00'}),
        }
        labels = {
            'title': 'Название вакансии',
            'salary_min': 'Зарплата от (₽)',
            'salary_max': 'Зарплата до (₽)',
            'company': 'Компания',
            'description': 'Описание',
            'skills': 'Требуемые навыки',
            'contact_email': 'Email для откликов',
            'contact_phone': 'Телефон для связи',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'skills':
                field.widget.attrs.update({'class': 'form-control'})

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'logo', 'city']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название компании',
            'description': 'Описание',
            'logo': 'Логотип',
            'city': 'Город',
        }