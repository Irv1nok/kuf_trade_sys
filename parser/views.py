import logging
from parser.forms import CategoriesForm, KufarItemsForm
from parser.models import KufarItems
from parser.services import parse_web_page

from background_task import background

from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)


def index(request):
    if request.method == 'POST':
        form = KufarItemsForm(request.POST)
        if form.is_valid():
            res = form.cleaned_data
            qs = KufarItems.objects.filter(cat_id=res['category'].pk)
            qs_filtered = None
            if qs:
                if res['title']:
                    qs_filtered = qs.filter(title__contains=res['title'])
                if res['price_min']:
                    qs_filtered = qs_filtered.filter(base_price__gte=res['price_min'])
                if res['price_max']:
                    qs_filtered = qs_filtered.filter(base_price__lte=res['price_max'])
                if res['deleted']:
                    qs_filtered = qs_filtered.filter(deleted=True)
                return render(request, 'detail.html', {'qs': qs_filtered})
            return render(request, 'index.html', {'form': form})
    else:
        form = KufarItemsForm()
    return render(request, 'index.html', {'form': form})


# @background(schedule=10)
def update_db(cat: dict, cat_id: int):
    parse_web_page(category=cat, cat_id=cat_id, update_db=True)


def parse_pages(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            cat = data['category']
            del cat.__dict__['_state']

            if data['test_connect']:  # Тест возможности получения данных.
                logger.debug('start test_connect')
                response = parse_web_page(category=cat.__dict__,
                                          cat_id=cat.id,
                                          test_conn=data['test_connect'])
                return render(request, 'response.html', {'response': response})

            elif not data['test_connect'] and not data['update_db']:
                logger.debug('start parse_web_page')
                # Парсинг всех данных с сохранением в бд.
                parse_web_page(category=cat.__dict__, cat_id=cat.id)

            elif data['update_db'] and not data['test_connect']:
                # Обновление данных в бд.
                logger.debug('start update_db')
                update_db(cat=cat.__dict__, cat_id=cat.id)

    else:
        form = CategoriesForm()
    return render(request, 'parser.html', {'form': form})


