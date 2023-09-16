from parser.models import Category

from django import forms


class CategoriesForm(forms.Form):
    category = forms.ModelChoiceField(label='Категория',
                                      queryset=Category.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control js-example-basic-single'}))

    test_connect = forms.BooleanField(required=False,
                                      help_text=' -- не использовать с поиском новых объявлений!')

    update_db = forms.BooleanField(required=False,
                                   label='Запуск обновления бд по интервалу')


class KufarItemsForm(forms.Form):
    category = forms.ModelChoiceField(label='Категория',
                                      queryset=Category.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control js-example-basic-single'}))

    title = forms.CharField(label='Название',
                            max_length=10,
                            required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control'}),
                            help_text='Введите название товара')
    city = forms.CharField(label='Город',
                           max_length=10,
                           required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),
                           help_text='Введите название Города')

    price_min = forms.IntegerField(label='Минимальная цена',
                                   widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   required=False)

    price_max = forms.IntegerField(label='Максимальная цена',
                                   widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   required=False)

    deleted = forms.BooleanField(label='Продано или нет',
                                 widget=forms.CheckboxInput(),
                                 required=False)
