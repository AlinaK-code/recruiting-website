from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

def trigger_error(request):
    return 1 / 0

urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), #для регистрации и управления лк
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', include('main.urls')), # для обычных страниц
    path('', include('main.api_urls')), #для API
    path('silk/', include('silk.urls', namespace='silk')), # для силк
]

