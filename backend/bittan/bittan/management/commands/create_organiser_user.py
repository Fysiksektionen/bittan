from django.core.management.base import BaseCommand

from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    def handle(self, **options):
        User.objects.filter(username="organiser").delete()
        Group.objects.filter(name="organisers").delete()

        organiser_user = User.objects.create_user("organiser", None, "organiser")

        organiser_group = Group.objects.create(name="organisers") 
        organiser_group.user_set.add(organiser_user)


