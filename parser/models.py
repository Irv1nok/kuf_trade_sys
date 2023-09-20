from django.db import models


class KufarItems(models.Model):
    id_item = models.IntegerField(unique=True)
    base_price = models.IntegerField(verbose_name="Стартовая цена")
    new_price = models.IntegerField(default=0, verbose_name="Новая цена")
    title = models.CharField(max_length=100, verbose_name="Название")
    city = models.CharField(max_length=20, verbose_name="Город")
    date = models.CharField(max_length=20, verbose_name="Дата создания, обновления в объявлении")
    url = models.CharField(max_length=200, verbose_name="Ссылка")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(null=True, verbose_name="Время обновления")
    deleted = models.BooleanField(default=False, verbose_name="Продано или нет")
    cat = models.ForeignKey('Category', default=0, on_delete=models.PROTECT, verbose_name="Категория")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар куфара'
        verbose_name_plural = 'Товары куфара'


class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name="Название")
    wrapper = models.CharField(max_length=50, verbose_name="Класс оболочка")
    title = models.CharField(max_length=50, verbose_name="Класс заголовка")
    price = models.CharField(max_length=50, verbose_name="Класс цены")
    country_date = models.CharField(max_length=50, verbose_name="Класс города и времени")
    next_page = models.CharField(max_length=100, verbose_name="Класс кнопки след.стр")
    url = models.CharField(max_length=200, verbose_name="Ссылка на категорию")
    accept_button = models.CharField(max_length=200, verbose_name="Класс кнопки 'Принять куки'")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'
