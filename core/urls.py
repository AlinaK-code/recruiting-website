from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')), # для обычных страниц
    path('', include('main.api_urls')), #для API
]
