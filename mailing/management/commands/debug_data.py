from django.core.management.base import BaseCommand
from mailing.models import Client, Message, Mailing
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Показывает все данные в базе'

    def handle(self, *args, **options):
        self.stdout.write("=== ПОЛЬЗОВАТЕЛИ ===")
        users = User.objects.all()
        if users:
            for user in users:
                self.stdout.write(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
        else:
            self.stdout.write("Нет пользователей")

        self.stdout.write("\n=== КЛИЕНТЫ ===")
        clients = Client.objects.all()
        if clients:
            for client in clients:
                self.stdout.write(f"ID: {client.id}, Email: {client.email}, Владелец: {client.owner.username}")
        else:
            self.stdout.write("Нет клиентов")

        self.stdout.write("\n=== СООБЩЕНИЯ ===")
        messages = Message.objects.all()
        if messages:
            for message in messages:
                self.stdout.write(f"ID: {message.id}, Тема: {message.subject}, Владелец: {message.owner.username}")
        else:
            self.stdout.write("Нет сообщений")

        self.stdout.write("\n=== РАССЫЛКИ ===")
        mailings = Mailing.objects.all()
        if mailings:
            for mailing in mailings:
                self.stdout.write(f"ID: {mailing.id}, Тема: {mailing.message.subject}, Клиентов: {mailing.clients.count()}, Владелец: {mailing.owner.username}")
        else:
            self.stdout.write("Нет рассылок")