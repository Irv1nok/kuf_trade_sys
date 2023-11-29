from bot.views import bot_send_msg_users

from django.urls import path


urlpatterns = [
    path('', bot_send_msg_users, name='home'),
]