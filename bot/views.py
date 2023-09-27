from django.http import HttpResponse


def bot_config(request):
    return HttpResponse('<h2>Бот запущен</h2>')
