from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, UserProfileForm
from main.models import Resume, Application
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    """Главная страница личного кабинета"""
    user = request.user
    
    resume = None
    try:
        resume = user.resume
    except Resume.DoesNotExist:
        pass
        
    # показ последние 5 откликов
    my_applications = Application.objects.filter(
        candidate=user
    ).select_related('vacancy').order_by('-applied_at')[:5]
    
    context = {
        'user': user,
        'resume': resume,
        'my_applications': my_applications,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    """Редактирование личных данных"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    return render(request, 'accounts/edit_profile.html', {'form': form})


class CustomLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile')
        
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_method = 'post'
        form.helper.add_input(Submit('submit', 'Войти', css_class='btn-success w-100'))
        return form