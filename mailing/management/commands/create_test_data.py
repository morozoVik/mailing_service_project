import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Client, Mailing, Message

User = get_user_model()


class Command(BaseCommand):
    help = "Создает тестовые данные для рассылок"

    def handle(self, *args, **options):
        password = os.getenv("TEST_USER_PASSWORD", "testpass123")

        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={"email": "test@example.com", "is_active": True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Создан тестовый пользователь: testuser / {password}"
                )
            )

        # Создаем клиентов
        clients_data = [
            {
                "email": "client1@example.com",
                "full_name": "Иван Иванов",
                "comment": "Постоянный клиент",
            },
            {
                "email": "client2@example.com",
                "full_name": "Петр Петров",
                "comment": "Новый клиент",
            },
            {
                "email": "client3@example.com",
                "full_name": "Мария Сидорова",
                "comment": "VIP клиент",
            },
        ]

        clients = []
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data["email"],
                defaults={
                    "full_name": client_data["full_name"],
                    "comment": client_data["comment"],
                    "owner": user,
                },
            )
            if created:
                clients.append(client)
                self.stdout.write(f"Создан клиент: {client.email}")

        message, created = Message.objects.get_or_create(
            subject="Тестовое сообщение",
            defaults={
                "body": "Это тестовое сообщение для проверки работы рассылки.",
                "owner": user,
            },
        )
        if created:
            self.stdout.write(f"Создано сообщение: {message.subject}")

        # Создаем рассылку
        mailing, created = Mailing.objects.get_or_create(
            message=message,
            defaults={
                "start_time": timezone.now(),
                "end_time": timezone.now() + timedelta(days=7),
                "status": Mailing.STATUS_CREATED,
                "owner": user,
            },
        )

        if created:
            # Добавляем клиентов к рассылке
            mailing.clients.set(clients)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Создана рассылка ID: {mailing.id} с {len(clients)} клиентами"
                )
            )
        else:
            self.stdout.write("Тестовые данные уже существуют")

        self.stdout.write(self.style.SUCCESS("Тестовые данные созданы успешно!"))
