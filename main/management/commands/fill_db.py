# main/management/commands/fill_db.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from main.models import (
    Skill, Company, CandidateProfile, RecruiterProfile,
    Vacancy, Application, Interview, Feedback
)

admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com', 
        'is_superuser': True, 
        'is_staff': True
    }
)
if not created:
    # если админ сущ, обнов права
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()


admin.set_password('123')
admin.save()

class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными (идемпотентно)'

    def handle(self, *args, **options):
        # 1. Суперпользователь
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True,
                'password': '' 
            }
        )
        if not admin.check_password('12345678'):
            admin.set_password('12345678')
            admin.save()

        # 2. Навыки
        skill_names = [
            'Python', 'Django', 'JavaScript', 'React', 'TypeScript',
            'PostgreSQL', 'MongoDB', 'Docker', 'Git', 'REST API',
            'SQL', 'HTML/CSS', 'Linux', 'Agile', 'English',
            'Node.js', 'Vue.js', 'AWS', 'Kubernetes', 'Figma'
        ]
        skills_map = {}
        for name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills_map[name] = skill

        # 3. Компании
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
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
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
            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                user.set_password('12345678')
                user.save()

            candidate_skills = [skills_map[s] for s in skill_list if s in skills_map]
            profile, _ = CandidateProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': full_name,
                    'phone': '+79991234567',
                    'portfolio_url': f'https://github.com/{username}'
                }
            )
            profile.skills.set(candidate_skills)
            candidates.append(user)

        # 6. Вакансии (используем title как уникальный ключ)
        vacancies_data = [
            ('Senior Python Developer', '5+ лет опыта, микросервисы, async', 180000, 300000, 'published', 0, ['Python', 'Django', 'PostgreSQL', 'Docker']),
            ('Django Developer', 'Опыт с DRF, PostgreSQL', 120000, 220000, 'published', 0, ['Python', 'Django', 'PostgreSQL', 'REST API']),
            ('React Developer', 'TypeScript, Redux, опыт 3+ года', 140000, 250000, 'published', 1, ['JavaScript', 'React', 'TypeScript', 'Redux']),
            ('DevOps Engineer', 'Docker, Kubernetes, CI/CD', 160000, 280000, 'published', 2, ['Docker', 'Kubernetes', 'Linux', 'AWS']),
            ('Data Scientist', 'Python, pandas, scikit-learn', 150000, 270000, 'published', 3, ['Python', 'SQL', 'Agile', 'English']),
            ('iOS Developer', 'Swift, SwiftUI, CoreData', 140000, 250000, 'published', 0, ['Swift', 'iOS', 'Mobile', 'Git']),
            ('Project Manager', 'Agile, Scrum, управление бюджетом', 140000, 250000, 'published', 0, ['Agile', 'Scrum', 'Management', 'English']),
            ('UI/UX Designer', 'Figma, прототипирование, usability', 100000, 180000, 'published', 5, ['Figma', 'UI/UX', 'Design', 'Prototyping']),
            ('Data Analyst', 'SQL, Power BI, Excel', 90000, 160000, 'published', 6, ['SQL', 'Power BI', 'Excel', 'Analytics']),
            ('QA Automation Engineer', 'Selenium, pytest, CI/CD', 110000, 200000, 'published', 3, ['Python', 'Selenium', 'Testing', 'CI/CD']),
            ('Frontend Team Lead', 'Управление командой, архитектура', 200000, 350000, 'published', 1, ['JavaScript', 'React', 'Leadership', 'Architecture']),
            ('ML Engineer', 'TensorFlow, PyTorch, NLP', 180000, 320000, 'published', 4, ['Python', 'ML', 'TensorFlow', 'NLP']),
            ('Cloud Architect (AWS)', 'Архитектура решений, AWS', 220000, 400000, 'published', 4, ['AWS', 'Cloud', 'Architecture', 'DevOps']),
            ('Security Specialist', 'Пентест, анализ уязвимостей', 150000, 280000, 'published', 2, ['Security', 'Pentest', 'Linux', 'Network']),
            ('Product Designer', 'Дизайн продуктов, user research', 120000, 210000, 'published', 5, ['Product Design', 'Research', 'Figma', 'UX']),
            ('Technical Support Engineer', 'Linux, сетевые технологии', 80000, 140000, 'published', 1, ['Linux', 'Networking', 'Support', 'SQL']),
            ('HR Manager (IT)', 'Подбор IT-специалистов', 90000, 160000, 'published', 2, ['HR', 'Recruiting', 'IT', 'Communication']),
            ('Digital Marketer', 'SEO, контекстная реклама', 85000, 150000, 'published', 5, ['SEO', 'Marketing', 'Analytics', 'Content']),
            ('Content Manager', 'Контент-стратегия, редактирование', 75000, 130000, 'published', 5, ['Content', 'Editing', 'Strategy', 'CMS']),
            ('Android Developer', 'Kotlin, Jetpack Compose', 130000, 240000, 'published', 0, ['Kotlin', 'Android', 'Mobile', 'Jetpack']),
            ('Flutter Developer', 'Кроссплатформенная разработка', 120000, 220000, 'published', 1, ['Flutter', 'Dart', 'Mobile', 'Cross-platform']),
            ('SRE Engineer', 'Мониторинг, отказоустойчивость', 170000, 300000, 'published', 2, ['SRE', 'Monitoring', 'Linux', 'Cloud']),
            ('Big Data Engineer', 'Spark, Hadoop, Kafka', 170000, 290000, 'published', 6, ['Spark', 'Hadoop', 'Kafka', 'Big Data']),
            ('System Analyst', 'Анализ требований, документация', 95000, 170000, 'published', 3, ['Analysis', 'Documentation', 'SQL', 'Business']),
            ('Junior Python Developer', 'Стажировка, обучение', 60000, 100000, 'draft', 0, ['Python', 'Git', 'SQL', 'Learning']),
        ]

        vacancies = []
        for i, (title, desc, min_sal, max_sal, status, company_idx, skill_names_list) in enumerate(vacancies_data):
            vacancy, created = Vacancy.objects.update_or_create(
                title=title,  
                defaults={
                    'description': desc,
                    'salary_min': min_sal,
                    'salary_max': max_sal,
                    'status': status,
                    'company': companies[company_idx],
                    'created_by': recruiters[i % len(recruiters)],
                    'contact_email': f'hr{i}@example.com',
                    'contact_phone': f'+799900000{i:02d}',
                }
            )

            selected_skills = [skills_map[s] for s in skill_names_list if s in skills_map]
            vacancy.skills.set(selected_skills)
            vacancies.append(vacancy)

        # тут использую фиксированные паттерны вместо random.choice/sample
        application_patterns = [
            # (candidate_idx, vacancy_idx, status, interview_days_offset, feedback_rating, feedback_comment)
            (0, 0, 'accepted', -5, 5, 'Отличный кандидат, принимаем!'),
            (0, 1, 'reviewed', None, None, None),
            (1, 2, 'interview_scheduled', 3, None, None),
            (1, 3, 'rejected', -3, 2, 'Недостаточно опыта'),
            (2, 0, 'submitted', None, None, None),
            (2, 4, 'accepted', -7, 4, 'Хорошие технические навыки'),
            (3, 7, 'interview_scheduled', 2, None, None),
            (3, 8, 'reviewed', None, None, None),
            (4, 3, 'accepted', -4, 5, 'Идеально подходит для DevOps'),
            (4, 9, 'rejected', -2, 1, 'Не прошел техническое интервью'),
            (5, 0, 'interview_scheduled', 5, None, None),
            (5, 10, 'submitted', None, None, None),
            (6, 2, 'accepted', -6, 4, 'Сильный фронтенд разработчик'),
            (6, 11, 'reviewed', None, None, None),
            (7, 0, 'rejected', -1, 2, 'Не соответствует требованиям'),
            (7, 12, 'interview_scheduled', 4, None, None),
            (8, 13, 'submitted', None, None, None),
            (8, 14, 'reviewed', None, None, None),
            (9, 8, 'accepted', -8, 5, 'Отличные аналитические способности'),
            (9, 15, 'interview_scheduled', 1, None, None),
            (10, 0, 'reviewed', None, None, None),
            (10, 16, 'submitted', None, None, None),
            (11, 7, 'accepted', -3, 4, 'Креативный дизайнер'),
            (11, 17, 'rejected', -2, 2, 'Портфолио не соответствует уровню'),
        ]

        for cand_idx, vac_idx, status, days_offset, rating, comment in application_patterns:
            if cand_idx >= len(candidates) or vac_idx >= len(vacancies):
                continue
            
            candidate = candidates[cand_idx]
            vacancy = vacancies[vac_idx]
            
            if vacancy.status != 'published' and status != 'submitted':
                continue

            app, _ = Application.objects.update_or_create(
                candidate=candidate,
                vacancy=vacancy,
                defaults={'status': status}
            )

            if days_offset is not None:
                scheduled_at = timezone.now() + timedelta(days=days_offset)
                interview_format = 'online' if days_offset > 0 else 'offline'
                interview_status = 'scheduled' if days_offset > 0 else 'completed'
                
                interview, _ = Interview.objects.update_or_create(
                    application=app,
                    defaults={
                        'scheduled_at': scheduled_at,
                        'format': interview_format,
                        'status': interview_status,
                        'duration_minutes': 60,
                    }
                )

                if rating is not None and comment:
                    Feedback.objects.update_or_create(
                        interview=interview,
                        defaults={
                            'rating': rating,
                            'comments': comment,
                            'created_by': recruiters[vac_idx % len(recruiters)],
                        }
                    )

        self.stdout.write(self.style.SUCCESS(
            'База данных заполнена:\n'
            '- 7 компаний\n'
            '- 7 рекрутеров\n'
            '- 12 кандидатов\n'
            '- 25 вакансий\n'
            '- Отклики со всеми статусами\n'
            '- Собеседования и обратная связь'
        ))