import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class User(AbstractUser):
    """Кастомная модель пользователя с дополнительными полями"""

    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    avatar = models.ImageField(
        upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    country = models.CharField(max_length=100, blank=True, verbose_name="Страна")

    email = models.EmailField(unique=True, verbose_name="Email")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Модель профиля пользователя с ролями"""

    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, verbose_name="Пользователь"
    )

    ROLE_USER = "user"
    ROLE_MANAGER = "manager"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_USER, "Пользователь"),
        (ROLE_MANAGER, "Менеджер"),
        (ROLE_ADMIN, "Администратор"),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_USER, verbose_name="Роль"
    )
    email_verified = models.BooleanField(
        default=False, verbose_name="Email подтвержден"
    )
    blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def __str__(self):
        return f"Профиль {self.user.username}"

    @property
    def is_manager(self):
        return self.role in [self.ROLE_MANAGER, self.ROLE_ADMIN]

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        if instance.is_superuser:
            profile.role = Profile.ROLE_ADMIN
        elif instance.is_staff:
            profile.role = Profile.ROLE_MANAGER
        else:
            profile.role = Profile.ROLE_USER

        profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        profile = instance.profile
        if instance.is_superuser and profile.role != Profile.ROLE_ADMIN:
            profile.role = Profile.ROLE_ADMIN
            profile.save()
        elif instance.is_staff and profile.role != Profile.ROLE_MANAGER:
            profile.role = Profile.ROLE_MANAGER
            profile.save()


class EmailVerification(models.Model):
    """Модель для подтверждения email"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    token = models.UUIDField(
        default=uuid.uuid4, unique=True, verbose_name="Токен подтверждения"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    expires_at = models.DateTimeField(verbose_name="Дата истечения")

    class Meta:
        verbose_name = "верификация email"
        verbose_name_plural = "верификации email"

    def __str__(self):
        return f"Верификация для {self.user.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def create_verification(cls, user):
        """Создает запись верификации для пользователя"""
        expires_at = timezone.now() + timedelta(hours=24)
        return cls.objects.create(user=user, expires_at=expires_at)
