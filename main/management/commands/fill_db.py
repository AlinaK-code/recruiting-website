# docker-compose exec web python manage.py fill_db
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import (
    Skill, Company, CandidateProfile, RecruiterProfile, Vacancy, Application
)

class Command(BaseCommand):
    help = 'Команда заполняет БД тестовыми данными: компании, рекрутеры, кандидаты, вакансии, отклики'

    def handle(self, *args, **options):
        # создаю суперпользователя (если нет еще)
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_superuser': True, 'is_staff': True}
        )
        if created:
            admin.set_password('12345678')
            admin.save()

        # навыки
        skill_names = [
            'Python', 'Django', 'JavaScript', 'React', 'TypeScript',
            'PostgreSQL', 'MongoDB', 'Docker', 'Git', 'REST API',
            'SQL', 'HTML/CSS', 'Linux', 'Agile', 'English',
            'Node.js', 'Vue.js', 'AWS', 'Kubernetes', 'Figma'
        ]
        skills = []
        for name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills.append(skill)

        # компании
        companies_data = [
            ('IT-Company', 'Москва'),
            ('WebDev Solutions', 'Санкт-Петербург'),
            ('DataTech', 'Новосибирск'),
            ('SoftLab', 'Екатеринбург'),
            ('CodeMasters', 'Казань'),
            ('Digital Agency', 'Ростов-на-Дону'),
            ('Analytics Pro', 'Владивосток'),
        ]
        companies = []
        for name, city in companies:
            company, _ = Company.objects.get_or_create(
                name=name,
                defaults={'city': city, 'description': f'Компания {name}'}
            )
            companies.append(company)

        # рекрутеры
        recruiter_data = [
            ('Иванов Иван Иванович', 'recruiter1@it-company.com', 0),
            ('Петрова Анна Сергеевна', 'recruiter2@webdev.ru', 1),
            ('Сидоров Дмитрий Алексеевич', 'recruiter3@datatech.ru', 2),
            ('Кузнецова Елена Владимировна', 'recruiter4@softlab.ru', 3),
            ('Морозов Артём Олегович', 'recruiter5@codemasters.ru', 4),
            ('Волкова Мария Павловна', 'recruiter6@digital.agency', 5),
            ('Лебедев Никита Юрьевич', 'recruiter7@analytics.pro', 6),
        ]

        recruiters = []
        for full_name, email, company_idx in recruiter_data:
            username = email.split('@')[0]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password('12345678')
                user.save()

            profile, _ = RecruiterProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company': companies[company_idx],
                    'contact_person': full_name
                }
            )
            recruiters.append(user)

        # кандидаты
        candidate_data = [
            ('Смирнов Алексей Андреевич', 'alex.smirnov@email.com', ['Python', 'Django', 'PostgreSQL']),
            ('Козлова Дарья Игоревна', 'darya.kozlova@email.com', ['JavaScript', 'React', 'TypeScript']),
            ('Попов Михаил Викторович', 'mikhail.popov@email.com', ['Python', 'SQL', 'Linux']),
            ('Федорова Анастасия Романовна', 'nastya.fedorova@email.com', ['Figma', 'HTML/CSS', 'English']),
            ('Гусев Арсений Дмитриевич', 'arseniy.gusev@email.com', ['Node.js', 'MongoDB', 'Docker']),
            ('Васильева Полина Алексеевна', 'polina.vasilieva@email.com', ['Python', 'SQL', 'Agile']),
            ('Егоров Тимофей Степанович', 'timofey.egorov@email.com', ['React', 'TypeScript', 'Git']),
            ('Никитина София Максимовна', 'sofia.nikitina@email.com', ['Python', 'Django', 'REST API']),
            ('Орлов Илья Константинович', 'ilya.orlov@email.com', ['JavaScript', 'Vue.js', 'HTML/CSS']),
            ('Макарова Виктория Ильинична', 'vika.makarova@email.com', ['SQL', 'Power BI', 'Excel']),
        ]

        candidates = []
        for full_name, email, skill_list in candidate_data:
            username = email.split('@')[0]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password('12345678')
                user.save()

            # Находим навыки по названию
            candidate_skills = [s for s in skills if s.name in skill_list]

            profile, _ = CandidateProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': full_name,
                    'phone': '+7 (999) 123-45-67',
                    'portfolio_url': f'https://github.com/{username}'
                }
            )
            if candidate_skills:
                profile.skills.set(candidate_skills)

            candidates.append(user)

        # вакансии
        vacancies_data = [
            ('Senior Python Developer', '5+ лет опыта, микросервисы, async', 180000, 300000, 'published', 0),
            ('Django Developer', 'Опыт с DRF, PostgreSQL', 120000, 220000, 'published', 0),
            ('React Developer', 'TypeScript, Redux, опыт 3+ года', 140000, 250000, 'published', 1),
            ('DevOps Engineer', 'Docker, Kubernetes, CI/CD', 160000, 280000, 'published', 2),
            ('Data Scientist', 'Python, pandas, scikit-learn', 150000, 270000, 'published', 3),
            ('iOS Developer', 'Swift, SwiftUI, CoreData', 140000, 250000, 'published', 0),
            ('Project Manager', 'Agile, Scrum, управление бюджетом', 140000, 250000, 'published', 0),
            ('UI/UX Designer', 'Figma, прототипирование, usability', 100000, 180000, 'published', 5),
            ('Data Analyst', 'SQL, Power BI, Excel', 90000, 160000, 'published', 6),
            ('QA Automation Engineer', 'Selenium, pytest, CI/CD', 110000, 200000, 'published', 3),
            ('Junior Python Developer', 'Стажировка, обучение', 60000, 100000, 'draft', 0),
            ('Senior Python Developer', '5+ лет опыта, микросервисы, async', 180000, 300000, 'published', 0),
            ('Django Developer', 'Опыт с DRF, PostgreSQL', 120000, 220000, 'published', 0),
            ('React Developer', 'TypeScript, Redux, опыт 3+ года', 140000, 250000, 'published', 1),
            ('DevOps Engineer', 'Docker, Kubernetes, CI/CD', 160000, 280000, 'published', 2),
            ('Data Scientist', 'Python, pandas, scikit-learn', 150000, 270000, 'published', 3),
            ('iOS Developer', 'Swift, SwiftUI, CoreData', 140000, 250000, 'published', 0),
        ]

        vacancies = []
        for i, (title, desc, min_sal, max_sal, status, company_idx) in enumerate(vacancies_data):
            vacancy, created = Vacancy.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'salary_min': min_sal,
                    'salary_max': max_sal,
                    'status': status,
                    'company': companies[company_idx],
                    'created_by': recruiters[i % len(recruiters)],
                }
            )
            if created:
                # назначаю навыки
                start_idx = i % len(skills)
                selected_skills = skills[start_idx:start_idx+3] or skills[:3]
                vacancy.skills.set(selected_skills)
            vacancies.append(vacancy)

        # отклики
        application_statuses = ['submitted', 'reviewed', 'interview_scheduled']
        for i, candidate in enumerate(candidates):
            # Каждый кандидат откликается на 2-3 вакансии
            for j in range(2):
                vac_index = (i + j) % len(vacancies)
                if vacancies[vac_index].status == 'published':
                    Application.objects.get_or_create(
                        candidate=candidate,
                        vacancy=vacancies[vac_index],
                        defaults={
                            'status': application_statuses[j % len(application_statuses)]
                        }
                    )

        self.stdout.write(self.style.SUCCESS(
            'База данных заполнена'
        ))