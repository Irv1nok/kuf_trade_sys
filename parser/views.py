from parser.forms import CategoriesForm
from parser.services import parse_web_page

from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def test_conn(request):
    form = CategoriesForm()
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            cat = data['category']
            response = parse_web_page(category=cat.__dict__, cat_id=cat.id, test_conn=True)
            return render(request, 'response.html', {'response': response})

    return render(request, 'test.html', {'form': form})


def parse_pages(request):
    form = CategoriesForm()
    if request.method == 'POST':

    return render(request, 'parser.html')


def bot_config(request):
    pass