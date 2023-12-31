from django.contrib import admin
from parser.models import Category, KufarItems

categories = ('name', 'title', 'price', 'city_date', 'wrapper', 'next_page', 'url_used', 'url_new',
              'accept_button', 'photo', 'count_ads', 'count_ad', 'process_parse_url',)


class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        model = Category

    list_display = ('id', ) + categories
    list_editable = categories
    list_display_links = None


class KufarItemsAdmin(admin.ModelAdmin):
    class Meta:
        model = KufarItems

    list_display = ('id_item', 'title', 'base_price', 'new_price', 'city', 'date',
                    'state', 'time_create', 'time_update', 'deleted', 'cat', 'url')

    list_filter = ('city', 'time_update', 'cat')


admin.site.register(Category, CategoryAdmin)
admin.site.register(KufarItems, KufarItemsAdmin)
