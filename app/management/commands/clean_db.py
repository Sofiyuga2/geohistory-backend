from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Pioneer.objects.all().delete()
        Discovery.objects.all().delete()
        CustomUser.objects.all().delete()