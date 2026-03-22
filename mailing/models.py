from django.conf import settings
from django.db import models
from django.utils import timezone


class Client(models.Model):
    """Модель получателя рассылки"""

    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Ф.И.О.")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"
        permissions = [
            ("can_view_all_clients", "Может просматривать всех клиентов"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Модель сообщения"""

    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        permissions = [
            ("can_view_all_messages", "Может просматривать все сообщения"),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Модель рассылки"""

    STATUS_CREATED = "created"
    STATUS_STARTED = "started"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_STARTED, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    ]

    start_time = models.DateTimeField(verbose_name="Время начала рассылки")
    end_time = models.DateTimeField(verbose_name="Время окончания рассылки")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус",
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    clients = models.ManyToManyField(Client, verbose_name="Получатели")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = ["-created_at"]
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_disable_mailings", "Может отключать рассылки"),
        ]

    def __str__(self):
        return f"Рассылка #{self.id} ({self.get_status_display()})"

    @property
    def is_active(self):
        """Проверяет, активна ли рассылка в данный момент"""
        now = timezone.now()
        return (
            self.status == self.STATUS_STARTED
            and self.start_time <= now <= self.end_time
        )

    def update_status(self):
        """Автоматически обновляет статус рассылки на основе времени"""
        now = timezone.now()

        if self.end_time <= now:
            self.status = self.STATUS_COMPLETED
        elif self.start_time <= now <= self.end_time:
            self.status = self.STATUS_STARTED
        elif now < self.start_time:
            self.status = self.STATUS_CREATED
        self.save()

    def get_successful_attempts_count(self):
        """Возвращает количество успешных попыток"""
        return self.mailingattempt_set.filter(
            status=MailingAttempt.STATUS_SUCCESS
        ).count()

    def get_failed_attempts_count(self):
        """Возвращает количество неуспешных попыток"""
        return self.mailingattempt_set.filter(
            status=MailingAttempt.STATUS_FAILED
        ).count()

    def get_total_attempts_count(self):
        """Возвращает общее количество попыток"""
        return self.mailingattempt_set.count()


class MailingAttempt(models.Model):
    """Модель попытки рассылки"""

    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Не успешно"),
    ]

    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="Рассылка"
    )
    attempt_time = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус попытки"
    )
    server_response = models.TextField(
        blank=True, verbose_name="Ответ почтового сервера"
    )

    class Meta:
        verbose_name = "попытка рассылки"
        verbose_name_plural = "попытки рассылки"
        ordering = ["-attempt_time"]

    def __str__(self):
        return f"Попытка {self.mailing} - {self.get_status_display()}"
