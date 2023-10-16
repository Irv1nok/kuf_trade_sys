from django.db import models


class BotUser(models.Model):
    telegram_id = models.IntegerField()


class Items(models.Model):
    id_item = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    category = models.IntegerField()
