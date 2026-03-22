import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from users.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Создает пользователя с ролью менеджера"

    def handle(self, *args, **options):
        password = os.getenv("MANAGER_PASSWORD", "manager123")

        user, created = User.objects.get_or_create(
            username="manager",
            defaults={"email": "manager@example.com", "is_staff": True},
        )
        if created:
            user.set_password(password)
            user.save()
            user.profile.role = Profile.ROLE_MANAGER
            user.profile.save()
            self.stdout.write(
                self.style.SUCCESS(f"Менеджер создан! Пароль: {password}")
            )
        else:
            self.stdout.write("Менеджер уже существует")
