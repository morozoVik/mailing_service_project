from django.core.management.base import BaseCommand

from mailing.services import send_mailing_by_id


class Command(BaseCommand):
    help = "Отправляет рассылку по ID"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int, help="ID рассылки для отправки")

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]

        self.stdout.write(f"Начало отправки рассылки ID {mailing_id}...")

        successful, failed = send_mailing_by_id(mailing_id)

        self.stdout.write(
            self.style.SUCCESS(
                f"Рассылка завершена. Успешно: {successful}, Неудачно: {failed}"
            )
        )
