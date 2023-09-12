from parser.forms import CategoriesForm
from parser.services import check_delete_or_sold_obj, parse_web_page

from background_task import background

from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


@background(schedule=10)
def update_db(cat: dict, cat_id: int):
    print('start update')
    parse_web_page(category=cat, cat_id=cat_id, update_db=True)


def parse_pages(request):
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            cat = data['category']
            del cat.__dict__['_state']

            if data['test_connect']:  # Тест возможности получения данных.
                response = parse_web_page(category=cat.__dict__,
                                          cat_id=cat.id,
                                          test_conn=data['test_connect'])
                return render(request, 'response.html', {'response': response})

            elif data['check_delete_or_sold']:
                check_delete_or_sold_obj(cat_id=cat.id)

            elif not data['test_connect'] and not data['check_delete_or_sold'] and not data['update_db']:
                # Парсинг всех данных с сохранением в бд.
                parse_web_page(category=cat.__dict__, cat_id=cat.id)

            elif data['update_db'] and not data['test_connect'] and not data['check_delete_or_sold']:
                update_db(cat=cat.__dict__, cat_id=cat.id)

    else:
        form = CategoriesForm()
    return render(request, 'parser.html', {'form': form})


