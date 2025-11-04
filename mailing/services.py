from django.core.mail import send_mail
from django.utils import timezone
from .models import Mailing, MailingAttempt, Client
import logging

logger = logging.getLogger(__name__)


def send_mailing(mailing):
    """
    Отправляет рассылку всем клиентам и создает записи о попытках
    """
    successful_sends = 0
    failed_sends = 0

    # Обновляем статус рассылки на "Запущена", если это первая отправка
    if mailing.status == Mailing.STATUS_CREATED:
        mailing.status = Mailing.STATUS_STARTED
        mailing.save()

    for client in mailing.clients.all():
        try:
            # Отправляем письмо
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email='ulb9@mail.ru',
                recipient_list=[client.email],
                fail_silently=False,
            )

            # Создаем запись об успешной попытке
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.STATUS_SUCCESS,
                server_response="Письмо успешно доставлено"
            )
            successful_sends += 1
            logger.info(f"Письмо успешно отправлено клиенту {client.email}")

        except Exception as e:
            # Создаем запись о неуспешной попытке
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(e)
            )
            failed_sends += 1
            logger.error(f"Ошибка отправки письма клиенту {client.email}: {str(e)}")

    # Проверяем, не завершилась ли рассылка по времени
    if mailing.end_time <= timezone.now():
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save()

    return successful_sends, failed_sends


def send_mailing_by_id(mailing_id):
    """
    Отправляет рассылку по ID
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        return send_mailing(mailing)
    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена")
        return 0, 0