import logging

from django.views.generic import ListView

from parser.forms import CategoriesForm, KufarItemsForm
from parser.models import KufarItems
from parser.services import parse_web_page

from background_task import background

from django.shortcuts import render

logger = logging.getLogger(__name__)


def index(request):
    form = KufarItemsForm()
    return render(request, 'parser/index.html', {'form': form})


class Searchlist(ListView):
    model = KufarItems
    template_name = 'parser/list.html'
    context_object_name = 'object'
    paginate_by = 25
    ordering = ['-date']

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category', None)
        title = self.request.GET.get('title', None)
        city = self.request.GET.get('city', None)
        pr_min = self.request.GET.get('price_min', None)
        pr_max = self.request.GET.get('price_max', None)
        deleted = self.request.GET.get('deleted', None)
        queryset = KufarItems.objects.filter(cat_id=category)
        if title:
            queryset = queryset.filter(title__contains=title)
        if city:
            queryset = queryset.filter(city__contains=city)
        if pr_min:
            try:
                queryset = queryset.filter(base_price__gte=int(pr_min))
            except ValueError:
                logger.error('wrong request price_min filter')
                pass
        if pr_max:
            try:
                queryset = queryset.filter(base_price__lte=int(pr_max))
            except ValueError:
                logger.error('wrong request price_max filter')
                pass
        if deleted == 'on':
            queryset = queryset.filter(deleted=True)
        return queryset

    def urlencode_filter(self):
        qd = self.request.GET.copy()
        qd.pop(self.page_kwarg, None)
        return qd.urlencode()


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
                return render(request, 'parser/response.html', {'response': response})

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
    return render(request, 'parser/parser.html', {'form': form})


