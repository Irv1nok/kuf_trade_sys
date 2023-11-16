from bot.models import BotUser, FavoritesItems, SearchItems

from django.contrib import admin




class BotUserAdmin(admin.ModelAdmin):
    class Meta:
        model = BotUser
        list_display = ('telegram_id', 'name',)
        list_editable = ('telegram_id', 'name')


class FavoritesItemsAdmin(admin.ModelAdmin):
    class Meta:
        model = FavoritesItems
        list_display = ('pk_item',)
        list_editable = ('pk_item',)


class SearchItemsAdmin(admin.ModelAdmin):
    class Meta:
        model = SearchItems
        list_display = ('category', 'title', 'min_price', 'max_price', 'city', )
        list_editable = ('category', 'title', 'min_price', 'max_price', 'city', )


admin.site.register(BotUser, BotUserAdmin)
admin.site.register(FavoritesItems, FavoritesItemsAdmin)
admin.site.register(SearchItems, SearchItemsAdmin)
