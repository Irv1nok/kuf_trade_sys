import logging

from parser.forms import CategoriesForm, KufarItemsForm
from parser.models import KufarItems
from parser.services import get_new_updates_in_categories, get_all_data_in_category, get_test_data

from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

logger = logging.getLogger(__name__)


def index(request):
    form = KufarItemsForm()
    return render(request, 'parser/index.html', {'form': form})


def parse_pages(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            cat = data['category']
            if data['update_db'] and not data['test_connect']:  # Создать таску для получения обновлений всех категорий.
                get_new_updates_in_categories(schedule=10, repeat=1800, priority=2)
                return redirect('parse_pages')

            if not data['category']:  # Проверяем наличие категории в запросе.
                return render(request, 'parser/parser.html', {'form': form})

            if data['test_connect'] and not data['update_db']:  # Тест возможности получения данных.
                response = get_test_data(category=cat.__dict__,
                                         cat_id=cat.id,
                                         test_conn=data['test_connect'])
                return render(request, 'parser/response.html', {'response': response})

            if not data['test_connect'] and not data['update_db']:
                del cat.__dict__['_state']  # <-- Вызывает background tasks json data error.
                get_all_data_in_category(category=cat.__dict__,
                                         cat_id=cat.id,
                                         schedule=20,
                                         repeat=14400
                                         )  # Парсинг всех данных , schedule=10, repeat=10800
                messages.success(request, 'Сохранено')

    else:
        form = CategoriesForm()
    return render(request, 'parser/parser.html', {'form': form})


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
            return queryset.filter(deleted=True).order_by('-time_create')

        return queryset.filter(deleted=False).order_by('-date')

    def urlencode_filter(self):
        qd = self.request.GET.copy()
        qd.pop(self.page_kwarg, None)
        return qd.urlencode()


class ItemDetailView(DetailView):
    model = KufarItems
    template_name = 'parser/detail.html'


def about(request):
    return render(request, 'parser/about.html')
