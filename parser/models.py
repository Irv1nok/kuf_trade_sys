from django.db import models
from django.urls import reverse


class KufarItems(models.Model):

    base_price = models.IntegerField(verbose_name='Стартовая цена')
    cat = models.ForeignKey('Category', null=True, db_index=True, on_delete=models.PROTECT, verbose_name='Категория')
    city = models.CharField(max_length=30, verbose_name='Город')
    date = models.CharField(max_length=20, verbose_name='Дата в объявлении')
    deleted = models.BooleanField(default=False, verbose_name='Продано или нет')
    id_item = models.IntegerField(db_index=True)
    in_favorites = models.BooleanField(default=False, verbose_name='В избранном или нет')
    new_price = models.IntegerField(default=0, verbose_name='Новая цена')
    photo_url = models.TextField(null=True, blank=True)
    state = models.BooleanField(null=True, verbose_name='Состояние: новое или б/у')
    title = models.CharField(max_length=100, verbose_name='Название')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(null=True, blank=True, verbose_name='Время обновления')
    url = models.TextField(verbose_name='Ссылка на товар')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('parser:item-detail', kwargs={'pk': self.id})

    class Meta:
        verbose_name = 'Товар куфара'
        verbose_name_plural = 'Товары куфара'


class Category(models.Model):
    accept_button = models.CharField(max_length=200, blank=True, null=True, verbose_name='Класс кнопки Принять куки')
    city_date = models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс города и времени')
    count_ad = models.IntegerField(default=0)
    count_ads = models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс количества объявлений')
    next_page = models.CharField(max_length=100, blank=True, null=True, verbose_name='Класс кнопки след.стр')
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Название')
    price = models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс цены')
    photo = models.CharField(blank=True, null=True, verbose_name='Класс фото')
    process_parse_url = models.TextField(blank=True, null=True,
                                         help_text='Ссылка на предыдущую страницу в драйвере парсера')
    state = models.BooleanField(null=True, blank=True)
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс заголовка')
    url_used = models.CharField(blank=True, null=True, verbose_name='Ссылка на категорию б/у товаров')
    url_new = models.CharField(blank=True, null=True, verbose_name='Ссылка на категорию новых товаров')
    wrapper = models.CharField(max_length=50, blank=True, null=True, verbose_name='Класс оболочка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'

