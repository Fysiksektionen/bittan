from django.core.management.base import BaseCommand
import datetime
from bittan.models import Payment
from bittan.models.payment import PaymentStatus

def run_cleaner():
    NOW = datetime.datetime.now()
    for payment in Payment.objects.filter(
        status = PaymentStatus.RESERVED,
        expires_at__lte = NOW,
        payment_started = False
    ):
        payment.status = PaymentStatus.FAILED_EXPIRED_RESERVATION
        payment.save()

class Command(BaseCommand):
    help = "Run the cleaner. Changes the status of expired payments."

    def handle(self, *args, **options):
        run_cleaner()
