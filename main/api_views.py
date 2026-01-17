from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from .models import Vacancy, Application
from .serializers import VacancySerializer, ApplicationSerializer


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
        # Фильтр по GET-параметрам
        min_salary = request.query_params.get('min_salary', 100000)
        return Response(
            VacancySerializer(
                Vacancy.objects.filter(salary_min__gte=min_salary),
                many=True
            ).data
        )

    # 2 кастомных Q-запросов  
    @action(detail=False, methods=['get'])
    def advanced_search_1(self, request):
        # Вакансии (опубликованы ИЛИ мои) И НЕ закрытые
        user = request.user
        queryset = Vacancy.objects.filter(
            (Q(status='published') | Q(created_by=user)) & ~Q(status='closed')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def advanced_search_2(self, request):
        # Вакансии НЕ черновики И (зарплата от 100000 ИЛИ созданы мной)
        user = request.user
        queryset = Vacancy.objects.filter(
            ~Q(status='draft') & (Q(salary_min__gte=100000) | Q(created_by=user))
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # 'OR' Q-запрос:
    @action(detail=False, methods=['get'])
    def complex_search(self, request):
        #  опубликованные ИЛИ созданные мной
        user = request.user
        queryset = Vacancy.objects.filter(
            Q(status='published') | Q(created_by=user)
        )
        return Response(VacancySerializer(queryset, many=True).data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        # Закрыть вакансию
        vacancy = self.get_object()
        vacancy.status = 'closed'
        vacancy.save()
        return Response({'status': 'Вакансия закрыта'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        # получить историю изменений вакансии
        vacancy = self.get_object()
        history = vacancy.history.all()
        return Response([
            {
                'changed_by': getattr(h.history_user, 'email', 'System') if h.history_user else 'System',
                'date': h.history_date.isoformat(),
                'status': getattr(h, 'status', 'N/A')
            }
            for h in history
        ])
class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'vacancy']