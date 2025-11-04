from django.utils import timezone
from .models import Mailing


def update_mailing_statuses(request):
    """
    Автоматически обновляет статусы рассылок при каждом запросе
    """
    if request.user.is_authenticated:
        try:
            # Находим рассылки пользователя, которые нужно обновить
            user_mailings = Mailing.objects.filter(owner=request.user)
            for mailing in user_mailings:
                mailing.update_status()
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            pass

    return {}