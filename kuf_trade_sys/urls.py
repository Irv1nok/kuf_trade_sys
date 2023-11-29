from django.conf import settings
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('bot/', include(('bot.urls', 'bot'))),
    path('', include(('parser.urls', 'parser'))),
    path('account/', include(('accounts.urls', 'accounts'))),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
