from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .decorators import manager_required
from .forms import CustomUserCreationForm
from .models import EmailVerification, Profile

User = get_user_model()


def register(request):
    """Регистрация нового пользователя с подтверждением email"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.is_active = False
            user.save()

            if not hasattr(user, "profile"):
                Profile.objects.create(user=user)

            verification = EmailVerification.create_verification(user)

            send_verification_email(request, user, verification.token)

            messages.success(
                request, "Аккаунт создан! Проверьте вашу почту для подтверждения email."
            )
            return redirect("users:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


def send_verification_email(request, user, token):
    """Отправляет email с ссылкой для подтверждения"""
    verification_url = request.build_absolute_uri(
        reverse("users:verify_email", kwargs={"token": token})
    )

    subject = "Подтверждение email в сервисе рассылок"
    message = f"""
    Здравствуйте, {user.username}!

    Для подтверждения вашего email перейдите по ссылке:
    {verification_url}

    Ссылка действительна в течение 24 часов.

    С уважением,
    Команда сервиса рассылок
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_email(request, token):
    """Подтверждение email по токену"""
    try:
        verification = EmailVerification.objects.get(token=token)

        if verification.is_expired():
            messages.error(request, "Ссылка для подтверждения устарела.")
            return redirect("users:register")

        if verification.user.profile.email_verified:
            messages.info(request, "Email уже подтвержден.")
            return redirect("users:login")

        verification.user.is_active = True
        verification.user.save()
        verification.user.profile.email_verified = True
        verification.user.profile.save()

        verification.delete()

        messages.success(request, "Email успешно подтвержден! Теперь вы можете войти.")
        return redirect("users:login")

    except EmailVerification.DoesNotExist:
        messages.error(request, "Неверная ссылка подтверждения.")
        return redirect("users:register")


def custom_logout(request):
    """Кастомный выход из системы"""
    logout(request)
    return redirect("mailing:index")


@manager_required
def user_list(request):
    """Список всех пользователей для менеджеров"""
    users = User.objects.all().select_related("profile")
    return render(request, "users/user_list.html", {"users": users})


@manager_required
def toggle_user_block(request, user_id):
    """Блокировка/разблокировка пользователя"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        user.profile.blocked = not user.profile.blocked
        user.profile.save()
        action = "заблокирован" if user.profile.blocked else "разблокирован"
        messages.success(request, f"Пользователь {user.username} {action}")
    else:
        messages.error(request, "Нельзя заблокировать себя")
    return redirect("users:user_list")


@manager_required
def change_user_role(request, user_id):
    """Изменение роли пользователя"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        new_role = request.POST.get("role")
        if new_role in [choice[0] for choice in Profile.ROLE_CHOICES]:
            user.profile.role = new_role
            user.profile.save()
            messages.success(request, f"Роль пользователя {user.username} изменена")
    return redirect("users:user_list")


@login_required
def profile_view(request):
    """Просмотр профиля пользователя"""
    return render(request, "users/profile_view.html", {"user": request.user})


@login_required
def profile_edit(request):
    """Редактирование профиля пользователя"""
    if request.method == "POST":
        user = request.user
        user.phone = request.POST.get("phone")
        user.country = request.POST.get("country")
        user.save()
        messages.success(request, "Профиль успешно обновлен!")
        return redirect("users:profile_view")

    return render(request, "users/profile_edit.html")
