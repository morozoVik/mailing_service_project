from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def manager_required(view_func=None, redirect_field_name=None, login_url=None):
    """
    Декоратор для проверки, что пользователь является менеджером или администратором
    проверяет через профиль и через группы Django
    """

    def check_manager(user):
        if not user.is_authenticated:
            return False

        if hasattr(user, "profile") and user.profile.is_manager:
            return True

        if user.groups.filter(name="Менеджеры").exists():
            return True

        return False

    actual_decorator = user_passes_test(
        check_manager, login_url=login_url, redirect_field_name=redirect_field_name
    )

    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def admin_required(view_func=None, redirect_field_name=None, login_url=None):
    """
    Декоратор для проверки, что пользователь является администратором
    """

    def check_admin(user):
        if not user.is_authenticated:
            return False

        if hasattr(user, "profile") and user.profile.is_admin:
            return True

        return False

    actual_decorator = user_passes_test(
        check_admin, login_url=login_url, redirect_field_name=redirect_field_name
    )

    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


class ManagerRequiredMixin:
    """Миксин для проверки прав менеджера в классах"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")

        is_manager = (
            hasattr(request.user, "profile") and request.user.profile.is_manager
        ) or request.user.groups.filter(name="Менеджеры").exists()

        if not is_manager:
            raise PermissionDenied("Доступ только для менеджеров")

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin:
    """Миксин для проверки прав администратора в классах"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")

        if not (hasattr(request.user, "profile") and request.user.profile.is_admin):
            raise PermissionDenied("Доступ только для администраторов")

        return super().dispatch(request, *args, **kwargs)


def group_required(group_name):
    """
    Декоратор для проверки принадлежности к конкретной группе
    """

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("users:login")

            if not request.user.groups.filter(name=group_name).exists():
                raise PermissionDenied(f"Требуется группа: {group_name}")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
