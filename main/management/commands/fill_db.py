# main/management/commands/fill_db.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from main.models import (
    Skill, Company, CandidateProfile, RecruiterProfile,
    Vacancy, Application, Interview, Feedback
)

class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными: компании, рекрутеры, кандидаты, вакансии, отклики, собеседования, фидбэк'

    def handle(self, *args, **options):
        #1. Суперпользователь 
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_superuser': True, 'is_staff': True}
        )
        if created:
            admin.set_password('12345678')
            admin.save()

        # 2. Навыки
        skill_names = [
            'Python', 'Django', 'JavaScript', 'React', 'TypeScript',
            'PostgreSQL', 'MongoDB', 'Docker', 'Git', 'REST API',
            'SQL', 'HTML/CSS', 'Linux', 'Agile', 'English',
            'Node.js', 'Vue.js', 'AWS', 'Kubernetes', 'Figma'
        ]
        skills = [Skill.objects.get_or_create(name=name)[0] for name in skill_names]

        #3. Компании
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
        for name, city in companies_data:
            company, _ = Company.objects.get_or_create(
                name=name,
                defaults={'city': city, 'description': f'Компания {name}'}
            )
            companies.append(company)

        # 4. Рекрутеры 
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
                defaults={'company': companies[company_idx], 'contact_person': full_name}
            )
            recruiters.append(user)

        # 5. Кандидаты 
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
            ('Белов Артём Сергеевич', 'artem.belov@email.com', ['Python', 'FastAPI', 'Redis']),
            ('Громова Екатерина Дмитриевна', 'ekaterina.gromova@email.com', ['UI/UX', 'Figma', 'Adobe XD']),
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

        # 6. Вакансии (25 штук) 
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
            ('Frontend Team Lead', 'Управление командой, архитектура', 200000, 350000, 'published', 1),
            ('ML Engineer', 'TensorFlow, PyTorch, NLP', 180000, 320000, 'published', 4),
            ('Cloud Architect (AWS)', 'Архитектура решений, AWS', 220000, 400000, 'published', 4),
            ('Security Specialist', 'Пентест, анализ уязвимостей', 150000, 280000, 'published', 2),
            ('Product Designer', 'Дизайн продуктов, user research', 120000, 210000, 'published', 5),
            ('Technical Support Engineer', 'Linux, сетевые технологии', 80000, 140000, 'published', 1),
            ('HR Manager (IT)', 'Подбор IT-специалистов', 90000, 160000, 'published', 2),
            ('Digital Marketer', 'SEO, контекстная реклама', 85000, 150000, 'published', 5),
            ('Content Manager', 'Контент-стратегия, редактирование', 75000, 130000, 'published', 5),
            ('Android Developer', 'Kotlin, Jetpack Compose', 130000, 240000, 'published', 0),
            ('Flutter Developer', 'Кроссплатформенная разработка', 120000, 220000, 'published', 1),
            ('SRE Engineer', 'Мониторинг, отказоустойчивость', 170000, 300000, 'published', 2),
            ('Big Data Engineer', 'Spark, Hadoop, Kafka', 170000, 290000, 'published', 6),
            ('System Analyst', 'Анализ требований, документация', 95000, 170000, 'published', 3),
            ('Junior Python Developer', 'Стажировка, обучение', 60000, 100000, 'draft', 0),
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
                start_idx = i % len(skills)
                selected_skills = skills[start_idx:start_idx+4] or skills[:4]
                vacancy.skills.set(selected_skills)
            vacancies.append(vacancy)

        #  7. Отклики + Собеседования + Фидбэк 
        from random import choice, sample

        all_statuses = ['submitted', 'reviewed', 'interview_scheduled', 'accepted', 'rejected']
        formats = ['online', 'office']

        for candidate in candidates:
            # Каждый кандидат откликается на 3–5 вакансий
            target_vacancies = sample(vacancies, k=min(5, len(vacancies)))
            for vac in target_vacancies:
                if vac.status != 'published':
                    continue

                # Выбираем случайный статус
                status = choice(all_statuses)

                app, created = Application.objects.get_or_create(
                    candidate=candidate,
                    vacancy=vac,
                    defaults={'status': status}
                )

                # Если назначено собеседование — создаём его
                if status == 'interview_scheduled':
                    interview = Interview.objects.create(
                        application=app,
                        scheduled_at=timezone.now() + timedelta(days=choice([1, 2, 3, 7])),
                        format=choice(formats),
                        status='scheduled'
                    )

                    # Добавляем фидбэк (для части собеседований)
                    if choice([True, False]):
                        Feedback.objects.create(
                            interview=interview,
                            rating=choice([3, 4, 5]),
                            comments=f"Хороший кандидат. Рекомендую к найму.",
                            created_by=choice(recruiters)
                        )

                # Для принятых/отклонённых — тоже можно создать интервью в прошлом
                elif status in ['accepted', 'rejected']:
                    interview = Interview.objects.create(
                        application=app,
                        scheduled_at=timezone.now() - timedelta(days=choice([1, 3, 5])),
                        format=choice(formats),
                        status='completed' if status == 'accepted' else 'cancelled'
                    )
                    Feedback.objects.create(
                        interview=interview,
                        rating=choice([2, 3, 4, 5]) if status == 'accepted' else choice([1, 2]),
                        comments=f"{'Принят' if status == 'accepted' else 'Отклонён'} по результатам собеседования.",
                        created_by=choice(recruiters)
                    )

        self.stdout.write(self.style.SUCCESS(
            'База данных заполнена:\n'
            '- 7 компаний\n'
            '- 7 рекрутеров\n'
            '- 12 кандидатов\n'
            '- 25 вакансий\n'
            '- Отклики со всеми статусами\n'
            '- Собеседования (назначенные и завершённые)\n'
            '- Обратная связь'
        ))