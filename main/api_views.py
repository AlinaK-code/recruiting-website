from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .permissions import IsResumeOwnerOrAdmin, IsOwnerOrAdmin, IsReviewOwnerOrAdmin
from django.db.models import Count, Avg, Q, QuerySet
from .models import Vacancy, Application, Resume, Review
from .serializers import VacancySerializer, ApplicationSerializer, ResumeSerializer, ReviewSerializer


class VacancyViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления вакансиями через REST API
    """
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # 1) фильтр по именованным аргументам, например http://127.0.0.1:8000/api/vacancies/?company=7
    filterset_fields = ['company', 'status'] 
    # 2) SearchFilter, например http://127.0.0.1:8000/api/vacancies/?search=Python         
    search_fields = ['title', 'description']
    # 3)  фильтр для ранжирования, пример http://127.0.0.1:8000/api/vacancies/?ordering=salary_min
    ordering_fields = ['created_at', 'salary_min']
    # подключаю права доступа 
    permission_classes = [IsOwnerOrAdmin] 

    # 4) фильтр по текущему пользователю
    def get_queryset(self) -> QuerySet[Vacancy]:
        """
        Возвращает оптимизированный queryset с аннотациями
        фильтрует вакансии по статусу и правам пользователя
        
        Returns:
            QuerySet[Vacancy]: Отфильтрованный набор вакансий
        """
        user = self.request.user
        # оптимизированыый qs
        qs = Vacancy.objects.select_related('company', 'created_by').prefetch_related('skills')

        # аннотации для вычисления доп. данных
        qs = qs.annotate(
            applications_count=Count('applications'),
            avg_feedback_rating=Avg('applications__interview__feedback__rating')
        )

        if user.is_authenticated:
            # авторизованный пользователь видит все опубликованные вакансии и свои черновики
            return qs.filter(Q(status='published') | Q(created_by=user))
         # Гость видит только опубликованные
        return qs.filter(status='published') 

    def perform_create(self, serializer: VacancySerializer) -> None:
        """
        Сохраняет новую вакансию, назначая текущего пользователя автором.
        
        Args:
            serializer: Валидированный сериализатор вакансии
        """
        # автоматом назначает текущего пользователя автором вакансии
        # при создании через апишку
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def high_salary(self, request) -> Response:
        """
        Возвращает вакансии с зарплатой выше указанной.
        
        Args:
            request: HTTP запрос с параметром min_salary
            
        Returns:
            Response: Список высокооплачиваемых вакансий
        """
        # 5) фильтр по GET, например ток зп >= 150k http://127.0.0.1:8000/api/vacancies/high_salary/?min_salary=150000
        min_salary = request.query_params.get('min_salary', 100000)
        # используею self.filter_queryset, чтобы применить оптимизацию и аннотации
        base_qs = self.get_queryset().filter(salary_min__gte=min_salary)
        serializer = self.get_serializer(base_qs, many=True)
        return Response(serializer.data)

    # 2 кастомных Q-запросов  
    @action(detail=False, methods=['get'])
    def advanced_search_1(self, request)-> Response:
        """
        Возвращает вакансии, которые опубликованы (или созданы мной) 
        и при этом не находятся в статусе 'closed'
        
        Args:
            request: HTTP запрос
            
        Returns:
            Response: Список отфильтрованных вакансий
        """
        # Вакансии (опубликованы ИЛИ мои) И НЕ закрытые
        user = request.user
        queryset = Vacancy.objects.filter(
            (Q(status='published') | Q(created_by=user)) & ~Q(status='closed')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def advanced_search_2(self, request)-> Response:
        """
        Возвращает вакансии которые не
        черновики и (зарплата от 100000 или созданы мной)
        
        Args:
            request: HTTP запрос
            
        Returns:
            Response: Список отфильтрованных вакансий
        """
        user = request.user
        queryset = Vacancy.objects.filter(
            ~Q(status='draft') & (Q(salary_min__gte=100000) | Q(created_by=user))
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # 'OR' Q-запрос:
    @action(detail=False, methods=['get'])
    def complex_search(self, request)-> Response:
        """
        возвращает все опубликованные вакансии 
        или созданные текущим пользователем
        
        Args:
            request: HTTP запрос
            
        Returns:
            Response: Список вакансий
        """
        user = request.user
        queryset = Vacancy.objects.filter(
            Q(status='published') | Q(created_by=user)
        )
        return Response(VacancySerializer(queryset, many=True).data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None)-> Response:
        """
        закрывает вакансию
        
        Args:
            request: HTTP запрос
            pk: Первичный ключ вакансии
            
        Returns:
            Response: Подтверждение изменения статуса
        """
        vacancy = self.get_object()
        vacancy.status = 'closed'
        vacancy.save()
        return Response({'status': 'Вакансия закрыта'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None)-> Response:
        """
        Возвращает историю изменений конкретной вакансии 
        через django-simple-history
        
        Args:
            request: HTTP запрос
            pk: Первичный ключ вакансии
            
        Returns:
            Response: Список записей истории изменений
        """
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
    """
    ViewSet для управления откликами на вакансии
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'vacancy']

    def get_queryset(self):
        """
        Фильтрует отклики: рекрутер видит отклики на свои вакансии, 
        соискатель - только свои отклики.
        
        Returns:
            QuerySet[Application]: Отфильтрованный набор откликов
        """
        user = self.request.user
        # смотрю есть ли у пользователя статус рекрутer
        if hasattr(user, 'recruiter_profile') and user.recruiter_profile.exists():
            return super().get_queryset().filter(vacancy__created_by=user)
        return super().get_queryset().filter(candidate=user)
    
class ResumeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления резюме соискателей
    Пользователь может создавать и редактировать только своё резюме
    """
    serializer_class = ResumeSerializer
    permission_classes = [IsResumeOwnerOrAdmin] 

    def get_queryset(self):
        """Соискатель видит только своё резюме, админ — все."""
        user = self.request.user
        if user.is_staff:
            return Resume.objects.select_related('user').prefetch_related('skills')
        return Resume.objects.filter(user=user)

    def perform_create(self, serializer):
        """Назначает текущего пользователя автором резюме."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Запрещает редактирование чужого резюме."""
        if serializer.instance.user != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Вы можете редактировать только своё резюме")
        super().perform_update(serializer)

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления отзывами.
    Пользователь может оставлять отзывы только на опубликованные вакансии.
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrAdmin]

    def get_queryset(self):
        """Все могут читать отзывы, писать/редактировать — только автор или админ."""
        return Review.objects.select_related('user', 'vacancy__company')

    def perform_create(self, serializer):
        """Привязывает отзыв к пользователю и вакансии из данных запроса."""
        vacancy_id = self.request.data.get('vacancy') 
        if not vacancy_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Необходимо указать ID вакансии")
            
        serializer.save(user=self.request.user, vacancy_id=vacancy_id)
    @action(detail=False, methods=['get'], url_path='my-reviews')
    def my_reviews(self, request):
        """Получить все мои отзывы."""
        reviews = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)