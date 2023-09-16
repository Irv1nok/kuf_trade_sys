import logging

from django.core.paginator import Paginator

from parser.forms import CategoriesForm, KufarItemsForm
from parser.models import KufarItems
from parser.services import parse_web_page

from background_task import background

from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)
QS_FILTERED_ITEMS = None


def index(request):
    form = KufarItemsForm()
    return render(request, 'index.html', {'form': form})


def search_list_items(request):
    global QS_FILTERED_ITEMS
    if request.GET.get('category'):
        try:
            category = int(request.GET.get('category'))
        except ValueError:
            return redirect('/')
        title = request.GET.get('title', default=None)
        city = request.GET.get('city', default=None)
        pr_min = request.GET.get('price_min', default=None)
        pr_max = request.GET.get('price_max', default=None)
        deleted = request.GET.get('deleted')

        QS_FILTERED_ITEMS = KufarItems.objects.filter(cat_id=category)
        if QS_FILTERED_ITEMS:
            if title:
                QS_FILTERED_ITEMS = QS_FILTERED_ITEMS.filter(title__contains=title)
            if city:
                QS_FILTERED_ITEMS = QS_FILTERED_ITEMS.filter(city__contains=city)
            if pr_min:
                try:
                    QS_FILTERED_ITEMS = QS_FILTERED_ITEMS.filter(base_price__gte=int(pr_min))
                except ValueError:
                    pass
            if pr_max:
                try:
                    QS_FILTERED_ITEMS = QS_FILTERED_ITEMS.filter(base_price__lte=int(pr_max))
                except ValueError:
                    pass
            if deleted == 'on':
                QS_FILTERED_ITEMS = QS_FILTERED_ITEMS.filter(deleted=True)

    paginator = Paginator(QS_FILTERED_ITEMS.order_by('-date'), 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'list.html', {'page_obj': page_obj})


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


