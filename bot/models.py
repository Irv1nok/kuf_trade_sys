from django.db import models


class BotUser(models.Model):
    name = models.CharField(max_length=10)
    slots_for_favitems = models.PositiveIntegerField(default=5)
    slots_for_searchitems = models.PositiveIntegerField(default=2)
    telegram_id = models.BigIntegerField(unique=False)

    def __str__(self):
        return f'{self.telegram_id} {self.name}'

    class Meta:
        verbose_name = 'ID пользователя'
        verbose_name_plural = 'ID пользователей'


class FavoritesItems(models.Model):
    bot_user = models.ForeignKey('BotUser', on_delete=models.CASCADE)
    pk_item = models.IntegerField(unique=True)

    def __str__(self):
        return f'{self.pk_item}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class SearchItems(models.Model):
    bot_user = models.ForeignKey('BotUser', on_delete=models.CASCADE)
    category = models.IntegerField(null=True)
    city = models.CharField(max_length=30, null=True, blank=True, verbose_name='Город')
    min_price = models.PositiveIntegerField(null=True, blank=True)
    max_price = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name='Название')
    state = models.BooleanField(null=True, blank=True, verbose_name='Состояние')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Поиск товаров'
        verbose_name_plural = 'Поиск товаров'
