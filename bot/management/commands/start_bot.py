from bot.services import start_bot

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_bot()
