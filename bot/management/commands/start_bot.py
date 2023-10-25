import logging

from django.core.management.base import BaseCommand

from bot.handlers import bot


class Command(BaseCommand):
    logger = logging.getLogger(__name__)
    def handle(self, *args, **options):
        self.logger.info('Starting local bot...')
        bot.polling(none_stop=True, interval=0)
