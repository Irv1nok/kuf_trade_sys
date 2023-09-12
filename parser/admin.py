from django.contrib import admin
from parser.models import Category, KufarItems

categories = ('name', 'title', 'price', 'country_date', 'wrapper', 'next_page', 'url', 'accept_button')


class ParserAdmin(admin.ModelAdmin):
    class Meta:
        model = Category

    list_display = ('id', ) + categories
    list_editable = categories
    list_display_links = None


class KufarItemsAdmin(admin.ModelAdmin):
    class Meta:
        model = KufarItems

    list_display = ('title', 'base_price', 'new_price', 'country', 'date', 'time_create', 'time_update', 'deleted', 'cat')


admin.site.register(Category, ParserAdmin)
admin.site.register(KufarItems, KufarItemsAdmin)
