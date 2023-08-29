from django.contrib import admin
from parser.models import *

categories = ('name', 'title', 'price', 'country_date', 'wrapper', 'url', 'accept_button')


class ParserAdmin(admin.ModelAdmin):
    class Meta:
        model = Category

    list_display = ('id', ) + categories
    list_editable = categories
    list_display_links = None


admin.site.register(Category, ParserAdmin)
