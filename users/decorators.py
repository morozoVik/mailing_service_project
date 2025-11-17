from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from .models import Profile

def manager_required(view_func=None, redirect_field_name=None, login_url=None):
    """
    Декоратор для проверки, что пользователь является менеджером или администратором
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, 'profile') and u.profile.is_manager,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

def admin_required(view_func=None, redirect_field_name=None, login_url=None):
    """
    Декоратор для проверки, что пользователь является администратором
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, 'profile') and u.profile.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

class ManagerRequiredMixin:
    """Миксин для проверки прав менеджера в классах"""
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_manager):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin:
    """Миксин для проверки прав администратора в классах"""
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_admin):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)