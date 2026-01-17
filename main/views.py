# main/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Vacancy

class VacancyListView(ListView):
    model = Vacancy
    template_name = 'main/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 10

class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    fields = ['title', 'description', 'salary_min', 'salary_max', 'company', 'skills']
    template_name = 'main/vacancy_form.html'
    success_url = reverse_lazy('main:vacancy_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
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