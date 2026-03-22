from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailVerification, Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для кастомной модели пользователя"""

    model = User
    list_display = ("email", "username", "phone", "country", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "profile__role")
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "last_name", "phone", "country")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = ("email", "username", "phone")
    ordering = ("email",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "email_verified", "blocked")
    list_filter = ("role", "email_verified", "blocked")
    search_fields = ("user__email", "user__username")


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at")
    list_filter = ("created_at", "expires_at")
    search_fields = ("user__email", "user__username")
