# main/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Vacancy, Company
from .forms import VacancyForm 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .forms import CompanyForm
from .forms import ResumeForm
from .models import Resume

class HomeView(TemplateView):
    template_name = 'main/home.html'

class VacancyListView(ListView):
    model = Vacancy
    template_name = 'main/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10

    def get_queryset(self):
        return Vacancy.objects.filter(status='published').select_related('company', 'created_by')

class VacancyDetailView(DetailView):
    model = Vacancy
    template_name = 'main/vacancy_detail.html'
    context_object_name = 'vacancy'

    def get_queryset(self):
        qs = Vacancy.objects.select_related('company', 'created_by').prefetch_related('skills')
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return qs
        if user.is_authenticated:
            return qs.filter(Q(status='published') | Q(created_by=user))
        return qs.filter(status='published')

class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'main/vacancy_form.html'
    success_url = reverse_lazy('main:vacancy_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'published'
        return super().form_valid(form)
    def form_invalid(self, form):
        print("="*50)
        print("ОШИБКИ ФОРМЫ:", form.errors)
        print("="*50)
        return super().form_invalid(form)

class VacancyUpdateView(LoginRequiredMixin, UpdateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'main/vacancy_form.html'
    
    def get_success_url(self):
        return reverse_lazy('main:vacancy_detail', kwargs={'pk': self.object.pk})

class VacancyDeleteView(LoginRequiredMixin, DeleteView):
    model = Vacancy
    template_name = 'main/vacancy_confirm_delete.html'
    success_url = reverse_lazy('main:vacancy_list')

class CompanyListView(ListView):
    model = Company
    template_name = 'main/company_list.html'
    context_object_name = 'companies'


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'main/company_form.html'
    
    def get_object(self, queryset=None):
        """Получаем объект компании с проверкой прав."""
        obj = super().get_object(queryset)
        
        # Админ может редактировать любую компанию
        if self.request.user.is_staff:
            return obj
            
        # Рекрутер может редактировать ТОЛЬКО свою компанию
        if hasattr(self.request.user, 'recruiter_profile') and self.request.user.recruiter_profile:
            if obj.pk == self.request.user.recruiter_profile.company.pk:
                return obj
                
        # Все остальные — доступ запрещен
        raise PermissionDenied("У вас нет прав для редактирования этой компании.")
    
    def get_success_url(self):
        # После сохранения возвращаемся в профиль
        from django.urls import reverse_lazy
        return reverse_lazy('accounts:profile')
    
class ResumeCreateView(LoginRequiredMixin, CreateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'main/resume_form.html'
    
    def form_valid(self, form):
        # Автоматически привязываем резюме к текущему пользователю
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        from django.urls import reverse_lazy
        return reverse_lazy('accounts:profile')


class ResumeUpdateView(LoginRequiredMixin, UpdateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'main/resume_form.html'
    
    def get_object(self, queryset=None):
        """Защищаем редактирование: только владелец или админ."""
        obj = super().get_object(queryset)
        if obj.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Вы можете редактировать только своё резюме")
        return obj
    
    def get_success_url(self):
        from django.urls import reverse_lazy
        return reverse_lazy('accounts:profile')