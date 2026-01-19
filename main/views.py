from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Vacancy, Company

class HomeView(TemplateView):
    template_name = 'main/home.html'

class VacancyListView(ListView):
    model = Vacancy
    template_name = 'main/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10

    def get_queryset(self):
        return Vacancy.objects.filter(status='published')

class VacancyDetailView(DetailView):
    model = Vacancy
    template_name = 'main/vacancy_detail.html'
    context_object_name = 'vacancy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vacancy = self.object
        applications = vacancy.applications.all()
        interviews = []
        for app in applications:
            if hasattr(app, 'interview'):
                interviews.append(app.interview)
        context['applications'] = applications
        context['interviews'] = interviews
        return context
    

class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    fields = ['title', 'description', 'salary_min', 'salary_max', 'company', 'skills']
    template_name = 'main/vacancy_form.html'
    success_url = reverse_lazy('main:vacancy_list ')
    

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'published'
        return super().form_valid(form)

class VacancyUpdateView(LoginRequiredMixin, UpdateView):
    model = Vacancy
    fields = ['title', 'description', 'salary_min', 'salary_max', 'company', 'skills']
    template_name = 'main/vacancy_form.html'
    success_url = reverse_lazy('main:vacancy_list')

class VacancyDeleteView(LoginRequiredMixin, DeleteView):
    model = Vacancy
    template_name = 'main/vacancy_confirm_delete.html'
    success_url = reverse_lazy('main:vacancy_list')

class CompanyListView(ListView):
    model = Company
    template_name = 'main/company_list.html'
    context_object_name = 'companies'