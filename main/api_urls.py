from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import VacancyViewSet, ApplicationViewSet

router = DefaultRouter()
router.register(r'vacancies', VacancyViewSet)
router.register(r'applications', ApplicationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]