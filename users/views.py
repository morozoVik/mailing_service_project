from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout

from .decorators import manager_required
from .models import Profile


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)

            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('users:login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def custom_logout(request):
    """Кастомный выход из системы"""
    logout(request)
    return redirect('mailing:index')


@manager_required
def user_list(request):
    """Список всех пользователей для менеджеров"""
    users = User.objects.all().select_related('profile')
    return render(request, 'users/user_list.html', {'users': users})

@manager_required
def toggle_user_block(request, user_id):
    """Блокировка/разблокировка пользователя"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        user.profile.blocked = not user.profile.blocked
        user.profile.save()
        action = "заблокирован" if user.profile.blocked else "разблокирован"
        messages.success(request, f'Пользователь {user.username} {action}')
    else:
        messages.error(request, 'Нельзя заблокировать себя')
    return redirect('users:user_list')

@manager_required
def change_user_role(request, user_id):
    """Изменение роли пользователя"""
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        new_role = request.POST.get('role')
        if new_role in [choice[0] for choice in Profile.ROLE_CHOICES]:
            user.profile.role = new_role
            user.profile.save()
            messages.success(request, f'Роль пользователя {user.username} изменена')
    return redirect('users:user_list')