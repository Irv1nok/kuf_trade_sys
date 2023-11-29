import logging

from django.contrib.auth.decorators import login_required

from bot.bot_config import bot
from bot.models import BotUser

from django.shortcuts import render
from django.contrib import messages

logger = logging.getLogger(__name__)

def bot_send_msg_users(request):
    if request.method == 'POST':
        msg = request.POST.get('msg')
        users = BotUser.objects.all()
        for user in users:
            try:
                bot.send_message(user.telegram_id, text=f'*Администратор*: {msg} ⚠️', parse_mode='MARKDOWN')
            except Exception as ex:
                messages.error(request, 'Ошибка')
                logger.exception(f'Error bot_send_msg_users {ex}')

            else:
                messages.success(request, 'Успешно')
    return render(request, 'bot/index.html')
