from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Profile

class Command(BaseCommand):
    help = 'Создает пользователя с ролью менеджера'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='manager',
            defaults={'email': 'manager@example.com', 'is_staff': True}
        )
        if created:
            user.set_password('manager123')
            user.save()
            user.profile.role = Profile.ROLE_MANAGER
            user.profile.save()
            self.stdout.write(self.style.SUCCESS('Менеджер создан!'))