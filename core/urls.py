from django.contrib import admin
from django.urls import path, include

def trigger_error(request):
    return 1 / 0

urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('admin/', admin.site.urls),
    path('', include('main.urls')), # для обычных страниц
    path('', include('main.api_urls')), #для API
    path('silk/', include('silk.urls', namespace='silk')), # для силк
]

