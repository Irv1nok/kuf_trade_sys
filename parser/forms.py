from parser.models import Category

from django import forms


class CategoriesForm(forms.Form):
    category = forms.ModelChoiceField(label='Категория', queryset=Category.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control js-example-basic-single'}))
    test_connect = forms.BooleanField(required=False, help_text=' -- не использовать с поиском новых объявлений!')
    update_db = forms.BooleanField(required=False, label='Запуск парсинга новых объявлений по интервалу')
    check_delete_or_sold = forms.BooleanField(required=False, label='Запуск поиска проданных или удаленных товаров')
