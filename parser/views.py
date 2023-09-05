from django.shortcuts import render
from parser.forms import CategoriesForm
from parser.services import parse_web_page


def index(request):
    form = CategoriesForm()
    if request.method == 'POST':
        form = CategoriesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            cat = data['category']
            response = parse_web_page(category=cat.__dict__, cat_id=cat.id, test_conn=True)
            # print(response)
            return render(request, 'response.html', {'response': response})

    return render(request, 'home.html', {'form': form})
