from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('vacancies/', views.VacancyListView.as_view(), name='vacancy_list'),
    path('vacancies/create/', views.VacancyCreateView.as_view(), name='vacancy_create'),
    path('vacancies/<int:pk>/edit/', views.VacancyUpdateView.as_view(), name='vacancy_edit'),
    path('vacancies/<int:pk>/delete/', views.VacancyDeleteView.as_view(), name='vacancy_delete'),
]