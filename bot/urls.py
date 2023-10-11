from bot.views import bot_config

from django.urls import path


urlpatterns = [
    path('config/', bot_config, name='bot_config'),
]