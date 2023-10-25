from django.db import models


class BotUser(models.Model):
    telegram_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.telegram_id} {self.name}'

    class Meta:
        verbose_name = 'ID пользователя'
        verbose_name_plural = 'ID пользователей'


class FavoritesItems(models.Model):
    bot_user = models.ForeignKey(BotUser, on_delete=models.CASCADE, null=True, blank=True)
    pk_item = models.IntegerField(unique=True)

    def __str__(self):
        return f'{self.pk_item}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
