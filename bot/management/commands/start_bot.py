import logging

from bot.handlers import bot

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        self.logger.info('Starting local bot...')
        bot.infinity_polling()
