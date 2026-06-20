from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import VacancyViewSet, ApplicationViewSet

app_name = 'main'

# роутер для автоматической генерации юрл в апи
router = DefaultRouter()
router.register(r'vacancies', VacancyViewSet, basename='vacancy-api')
router.register(r'applications', ApplicationViewSet, basename='application-api')

urlpatterns = [
 path('', views.HomeView.as_view(), name='home'),
    
    # Вакансии
    path('vacancies/', views.VacancyListView.as_view(), name='vacancy_list'),
    path('vacancies/<int:pk>/', views.VacancyDetailView.as_view(), name='vacancy_detail'),
    path('vacancies/create/', views.VacancyCreateView.as_view(), name='vacancy_create'),
    path('vacancies/<int:pk>/edit/', views.VacancyUpdateView.as_view(), name='vacancy_edit'),
    path('vacancies/<int:pk>/delete/', views.VacancyDeleteView.as_view(), name='vacancy_delete'),
    
    # Компании
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    
    # эндпоинты для апи, что-то типа  /api/vacancies/, /api/vacancies/high_salary/, /api/applications/
    path('api/', include(router.urls)),
]