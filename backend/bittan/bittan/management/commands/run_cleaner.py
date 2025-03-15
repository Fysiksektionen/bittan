from django.core.management.base import BaseCommand
from django.utils import timezone
from bittan.models import Payment
from bittan.models.payment import PaymentStatus

def run_cleaner():
    NOW = timezone.now()
    Payment.objects.filter(
        status = PaymentStatus.RESERVED,
        expires_at__lte = NOW,
        payment_started = False
    ).update(
        status = PaymentStatus.FAILED_EXPIRED_RESERVATION
    )

class Command(BaseCommand):
    help = "Run the cleaner. Changes the status of expired payments."

    def handle(self, *args, **options):
        run_cleaner()
