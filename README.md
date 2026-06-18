# Сервис собеседований

## Запуск проекта
```
# сборка проекта
docker-compose up --build -d

# запуск миграций
docker-compose exec web python manage.py migrate

# наполнение бд тестовыми данными
docker-compose exec web python manage.py fill_db
```
## Сервис доступен по ссылке
http://127.0.0.1:8000/

## Админка
http://127.0.0.1:8000/admin

Курсовой проект выполнен: студенткой группы 241-321, Каматали Алиной