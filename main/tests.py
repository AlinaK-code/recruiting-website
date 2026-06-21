from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Vacancy, Company, Skill, Application

# чтобы заупустить тесты: (флаг -v 2 дает подробный вывод )
# docker-compose exec web python manage.py test main.tests -v 2

class VacancyModelTest(TestCase):
    """Тесты для модели Vacancy"""

    def setUp(self):
        self.company = Company.objects.create(name="Test Corp", city="Moscow")
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_create_vacancy_success(self):
        """Тест 1: Успешное создание вакансии"""
        vacancy = Vacancy.objects.create(
            title="Python Dev",
            description="Write code",
            salary_min=100000,
            salary_max=200000,
            company=self.company,
            created_by=self.user
        )
        self.assertEqual(vacancy.title, "Python Dev")
        self.assertEqual(Vacancy.objects.count(), 1)  

class VacancyAPITest(TestCase):
    """Тесты для REST API вакансий"""

    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="API Test Corp", city="SPb")
        self.skill = Skill.objects.create(name="Django")
        
        # пользователь-владелец
        self.owner = User.objects.create_user(
            username='owner', password='ownerpass'
        )
        # другой пользователь
        self.other = User.objects.create_user(
            username='other', password='otherpass'
        )
        
        # тестовая вакансия
        self.vacancy = Vacancy.objects.create(
            title="Existing Vacancy",
            description="Desc",
            salary_min=50000,
            salary_max=100000,
            company=self.company,
            created_by=self.owner,
            status='published'
        )
        self.vacancy.skills.add(self.skill)

    def test_invalid_salary_range(self):
        """Тест 2: Валидация диапазона зарплат min > max в сериализаторе"""
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Bad Salary Job", "description": "Test",
            "salary_min": 200000, "salary_max": 100000,
            "company": self.company.id
        }
        response = self.client.post('/api/vacancies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Ошибка может быть в non_field_errors или привязана к полю
        self.assertTrue(
            'non_field_errors' in response.data or 
            any('зарплата' in str(v).lower() for v in response.data.values())
        )  

    def test_list_vacancies_public(self):
        """Тест 3: Публичный список вакансий возвращает 200"""
        response = self.client.get('/api/vacancies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_vacancy_unauthorized(self):
        """Тест 4: Создание вакансии без авторизации запрещено"""
        data = {
            "title": "New Job",
            "description": "Desc",
            "salary_min": 60000,
            "salary_max": 90000,
            "company": self.company.id
        }
        response = self.client.post('/api/vacancies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_vacancy_success(self):
        """Тест 5: Успешное создание вакансии авторизованным пользователем"""
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Junior Dev",
            "description": "Learn",
            "salary_min": 40000,
            "salary_max": 70000,
            "company": self.company.id
        }
        response = self.client.post('/api/vacancies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_by'], self.owner.id)

    def test_update_other_vacancy_forbidden(self):
        """Тест 6: Запрет на редактирование чужой вакансии"""
        self.client.force_authenticate(user=self.other)
        data = {"title": "Hacked Title"}
        response = self.client.put(
            f'/api/vacancies/{self.vacancy.id}/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_own_vacancy_success(self):
        """Тест 7: Успешное редактирование своей вакансии"""
        self.client.force_authenticate(user=self.owner)
        data = {"title": "Updated Title"}
        response = self.client.patch(
            f'/api/vacancies/{self.vacancy.id}/', data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vacancy.refresh_from_db()
        self.assertEqual(self.vacancy.title, "Updated Title")

    def test_filter_by_status(self):
        """Тест 8: Фильтрация вакансий по статусу"""
        response = self.client.get('/api/vacancies/?status=published')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должна быть хотя бы одна опубликованная вакансия
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_search_vacancies(self):
        """Тест 9: Поиск вакансий по названию"""
        response = self.client.get('/api/vacancies/?search=Existing')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Existing Vacancy")

    def test_annotations_applications_count(self):
        """Тест 10: Проверка работы аннотаций (к-во откликов)"""
        # создаю отклик на существующую вакансию
        applicant = User.objects.create_user(username='applicant', password='pass')
        Application.objects.create(
            vacancy=self.vacancy,
            candidate=applicant,
            status='submitted'
        )
        
        # тут получаю список вакансий
        response = self.client.get('/api/vacancies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # ищу эту вакансию в ответе и проверяю поле applications_count
        found_vacancy = None
        for v in response.data['results']:
            if v['id'] == self.vacancy.id:
                found_vacancy = v
                break
                
        self.assertIsNotNone(found_vacancy)
        self.assertEqual(found_vacancy['applications_count'], 1)