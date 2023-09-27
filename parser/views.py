import logging
from parser.forms import CategoriesForm, KufarItemsForm
from parser.models import KufarItems
from parser.services import parse_web_page

from background_task import background

from django.shortcuts import render
from django.views.generic import ListView


logger = logging.getLogger(__name__)


def index(request):
    form = KufarItemsForm()
    return render(request, 'parser/index.html', {'form': form})


class SearchItemsList(ListView):
    model = KufarItems
    template_name = 'parser/list.html'
    context_object_name = 'object'
    paginate_by = 25

    def get_queryset(self):
        deleted = self.request.GET.get('deleted', None)
        queryset = KufarItems.objects.filter(cat_id=self.request.GET.get('category', None))

        if title := self.request.GET.get('title', None):
            queryset = queryset.filter(title__contains=title)

        if city := self.request.GET.get('city', None):
            queryset = queryset.filter(city__contains=city)

        if pr_min := self.request.GET.get('price_min', None):
            try:
                queryset = queryset.filter(base_price__gte=int(pr_min))
            except ValueError:
                logger.error('wrong type request price_min')

        if pr_max := self.request.GET.get('price_max', None):
            try:
                queryset = queryset.filter(base_price__lte=int(pr_max))
            except ValueError:
                logger.error('wrong type request price_max')

        if deleted == 'on':
            return queryset.filter(deleted=True).order_by('-date')
        else:
            return queryset.filter(deleted=False).order_by('time_update')

    def urlencode_filter(self):
        qd = self.request.GET.copy()
        qd.pop(self.page_kwarg, None)
        return qd.urlencode()


@background(schedule=60)
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

            # elif not data['test_connect'] and not data['update_db']:
            #     logger.debug('start parse_web_page')
            #     # Парсинг всех данных с сохранением в бд.
            #     parse_web_page(category=cat.__dict__, cat_id=cat.id)

            elif data['update_db'] and not data['test_connect']:
                # Обновление данных в бд.
                logger.debug('start update_db')
                update_db(cat=cat.__dict__, cat_id=cat.id)

    else:
        form = CategoriesForm()
    return render(request, 'parser/parser.html', {'form': form})


