from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from main.models import Company, CandidateProfile, RecruiterProfile

ROLE_CHOICES = [
    ('candidate', 'Соискатель'),
    ('recruiter', 'Работодатель'),
]


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации с выбором роли."""
    email = forms.EmailField(required=True, label='Email')
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label='Я регистрируюсь как',
        widget=forms.RadioSelect,
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False,
        label='Компания',
        empty_label='Выберите компанию',
    )
    contact_person = forms.CharField(
        required=False,
        max_length=255,
        label='Контактное лицо',
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'company', 'contact_person')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Зарегистрироваться', css_class='btn-primary btn-lg w-100')
        )

        self.fields['username'].label = 'Логин'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company = cleaned_data.get('company')
        contact_person = cleaned_data.get('contact_person')

        if role == 'recruiter':
            if not company:
                self.add_error('company', 'Работодатель должен выбрать компанию.')
            if not contact_person:
                self.add_error(
                    'contact_person',
                    'Укажите контактное лицо для связи с кандидатами.',
                )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if not commit:
            return user

        role = self.cleaned_data['role']
        if role == 'candidate':
            CandidateProfile.objects.create(
                user=user,
                full_name=user.get_full_name() or user.username,
                contact_email=user.email,
            )
        elif role == 'recruiter':
            RecruiterProfile.objects.create(
                user=user,
                company=self.cleaned_data['company'],
                contact_person=self.cleaned_data['contact_person'],
            )
        return user


class UserProfileForm(forms.ModelForm):
    """Форма редактирования личных данных"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Сохранить изменения', css_class='btn-success'))

        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'Email'
