import logging
import os

from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)


def send_mailing(mailing):
    """
    Отправляет рассылку всем клиентам и создает записи о попытках
    """
    successful_sends = 0
    failed_sends = 0

    if mailing.status == Mailing.STATUS_CREATED:
        mailing.status = Mailing.STATUS_STARTED
        mailing.save()

    from_email = os.getenv("DEFAULT_FROM_EMAIL", "ulb9@mail.ru")

    for client in mailing.clients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=from_email,
                recipient_list=[client.email],
                fail_silently=False,
            )

            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.STATUS_SUCCESS,
                server_response="Письмо успешно доставлено",
            )
            successful_sends += 1
            logger.info(f"Письмо успешно отправлено клиенту {client.email}")

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(e),
            )
            failed_sends += 1
            logger.error(f"Ошибка отправки письма клиенту {client.email}: {str(e)}")

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
