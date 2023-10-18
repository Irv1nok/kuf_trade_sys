from django.contrib import admin

from bot.models import BotUser, Items


class BotUserAdmin(admin.ModelAdmin):
    class Meta:
        model = BotUser
        list_display = ('telegram_id', 'name',)
        list_editable = ('telegram_id', 'name')


class ItemsAdmin(admin.ModelAdmin):
    class Meta:
        model = Items
        list_display = ('pk_item', 'category',)
        list_editable = ('pk_item', 'category',)


admin.site.register(BotUser, BotUserAdmin)
admin.site.register(Items, ItemsAdmin)
