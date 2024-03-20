from django.core.management.base import BaseCommand
from bittan.models import TicketType

def run_cleaner():
    TicketType.objects.create(price=69, title="Cleanerbiljett", description="Biljett skapad av Cleaner")
    print("Cleaner was run")

class Command(BaseCommand):
    help = "Run cleaner."

    def handle(self, *args, **options):
        run_cleaner()
