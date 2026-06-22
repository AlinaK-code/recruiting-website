# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, UserProfileForm
from main.models import Resume, Application, Vacancy, User  # Добавлен User
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count


def register_view(request):
    """Регистрация нового пользователя с назначением роли."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    """Главная страница личного кабинета."""
    user = request.user

    # Получаем резюме соискателя
    resume = None
    try:
        resume = user.resume
    except Resume.DoesNotExist:
        pass

    # Отклики соискателя
    my_applications = (
        Application.objects.filter(candidate=user)
        .select_related("vacancy", "vacancy__company")
        .order_by("-applied_at")[:5]
    )

    # Данные для рекрутера
    recruiter_applications = None
    my_vacancies = None
    if hasattr(user, "recruiter_profile") and user.recruiter_profile:
        recruiter_applications = (
            Application.objects.filter(vacancy__created_by=user)
            .select_related("vacancy", "candidate")
            .order_by("-applied_at")[:5]
        )

        my_vacancies = user.vacancy_set.select_related("company").order_by(
            "-created_at"
        )[:5]

    # АНАЛИТИКА ДЛЯ АДМИНА
    admin_stats = None
    if user.is_staff:
        total_vacancies = Vacancy.objects.count()
        published_vacancies = Vacancy.objects.filter(status="published").count()
        total_applications = Application.objects.count()
        active_users = User.objects.filter(is_active=True).count()

        # Топ-3 популярных вакансии по откликам (используем аннотацию!)
        top_vacancies = (
            Vacancy.objects.select_related("company")
            .annotate(apps_count=Count("applications"))
            .order_by("-apps_count")[:3]
        )

        admin_stats = {
            "total_vacancies": total_vacancies,
            "published_vacancies": published_vacancies,
            "total_applications": total_applications,
            "active_users": active_users,
            "top_vacancies": top_vacancies,
        }

    context = {
        "user": user,
        "resume": resume,
        "my_applications": my_applications,
        "recruiter_applications": recruiter_applications,
        "my_vacancies": my_vacancies,
        "is_recruiter": hasattr(user, "recruiter_profile")
        and bool(user.recruiter_profile),
        "is_candidate": hasattr(user, "candidate_profile")
        and bool(user.candidate_profile),
        "admin_stats": admin_stats,  # <-- Передаем статистику в шаблон
    }
    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile_view(request):
    """Редактирование личных данных"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "accounts/edit_profile.html", {"form": form})


class CustomLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("accounts:profile")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_method = "post"
        form.helper.add_input(Submit("submit", "Войти", css_class="btn-success w-100"))
        return form


def update_application_status(request, pk):
    """Обработка кнопок Принять/Отклонить в ЛК рекрутера"""
    if request.method == "POST":
        application = Application.objects.get(pk=pk)

        # Проверка безопасности: рекрутер может менять статус только своих вакансий
        if application.vacancy.created_by != request.user and not request.user.is_staff:
            messages.error(request, "У вас нет прав управлять этим откликом.")
            return HttpResponseRedirect(reverse("accounts:profile"))

        new_status = request.POST.get("status")
        if new_status in ["accepted", "rejected"]:
            application.status = new_status
            application.save()
            messages.success(
                request,
                f"Статус отклика изменен на: {application.get_status_display()}",
            )

    return HttpResponseRedirect(reverse("accounts:profile"))
