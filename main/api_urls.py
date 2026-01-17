from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import VacancyViewSet

router = DefaultRouter()
router.register(r'vacancies', VacancyViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]