from django.core.management.base import BaseCommand
from bittan.models import Payment
from bittan.models.payment import PaymentStatus

def run_cleaner():
    for payment in Payment.objects.filter(
        status = PaymentStatus.RESERVED
    ):
        payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
        payment.save()

class Command(BaseCommand):
    help = "Run the cleaner. Changes the status of expired payments."

    def handle(self, *args, **options):
        run_cleaner()
