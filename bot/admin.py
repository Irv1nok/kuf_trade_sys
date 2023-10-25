from django.contrib import admin

from bot.models import BotUser, FavoritesItems


class BotUserAdmin(admin.ModelAdmin):
    class Meta:
        model = BotUser
        list_display = ('telegram_id', 'name',)
        list_editable = ('telegram_id', 'name')


class ItemsAdmin(admin.ModelAdmin):
    class Meta:
        model = FavoritesItems
        list_display = ('pk_item',)
        list_editable = ('pk_item',)


admin.site.register(BotUser, BotUserAdmin)
admin.site.register(FavoritesItems, ItemsAdmin)
