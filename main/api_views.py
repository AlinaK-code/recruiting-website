# main/api_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from .models import Vacancy
from .serializers import VacancySerializer

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'status']          # 1. Фильтр по именованным аргументам
    search_fields = ['title', 'description']         # 2. SearchFilter
    ordering_fields = ['created_at', 'salary_min']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # авторизованный пользователь видит все опубликованные вакансии и свои черновики
            return Vacancy.objects.filter(
                Q(status='published') | Q(created_by=user)
            )
        else:
            # Гость видит только опубликованные
            return Vacancy.objects.filter(status='published')

    @action(detail=False, methods=['get'])
    def high_salary(self, request):
        """4. Фильтр по GET-параметрам"""
        min_salary = request.query_params.get('min_salary', 100000)
        return Response(
            VacancySerializer(
                Vacancy.objects.filter(salary_min__gte=min_salary),
                many=True
            ).data
        )

    @action(detail=False, methods=['get'])
    def complex_search(self, request):
        """5. Сложный Q-запрос: опубликованные ИЛИ созданные мной"""
        user = request.user
        queryset = Vacancy.objects.filter(
            Q(status='published') | Q(created_by=user)
        )
        return Response(VacancySerializer(queryset, many=True).data)