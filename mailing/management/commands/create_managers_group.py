from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailing.models import Client, Mailing, Message


class Command(BaseCommand):
    help = "Создает группу Менеджеры с необходимыми правами"

    def handle(self, *args, **options):
        managers_group, created = Group.objects.get_or_create(name="Менеджеры")

        if created:
            content_types = [
                ContentType.objects.get_for_model(Client),
                ContentType.objects.get_for_model(Message),
                ContentType.objects.get_for_model(Mailing),
            ]

            for content_type in content_types:
                permissions = Permission.objects.filter(content_type=content_type)
                managers_group.permissions.add(*permissions)

            self.stdout.write(
                self.style.SUCCESS('Группа "Менеджеры" создана с правами доступа!')
            )
        else:
            self.stdout.write('Группа "Менеджеры" уже существует')
