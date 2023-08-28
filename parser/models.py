from django.db import models


class KufarItems(models.Model):
    id_item = models.CharField(max_length=100, unique=True)
    price = models.CharField(max_length=20, verbose_name='Цена')
    title = models.CharField(max_length=100, verbose_name='Название')
    country = models.CharField(max_length=20, verbose_name='Город')
    date = models.CharField(max_length=20, verbose_name='Дата создания, обновления')
    url = models.CharField(max_length=200, verbose_name='Ссылка')
    deleted = models.BooleanField()
    category = models.ForeignKey('Category', default=0, on_delete=models.PROTECT, verbose_name='Категория')

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    wrapper = models.CharField(max_length=50, verbose_name='Класс оболочка')
    title = models.CharField(max_length=50, verbose_name='Класс загаловка')
    price = models.CharField(max_length=50, verbose_name='Класс цены')
    country_date = models.CharField(max_length=50, verbose_name='Класс города и времени')
    url = models.CharField(max_length=200, verbose_name='Ксылка на категорию')
    accept_button = models.CharField(max_length=200, verbose_name="Класс кнопки 'Принять куки'")

    def __str__(self):
        return self.name
