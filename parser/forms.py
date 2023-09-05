from django import forms
from parser.models import Category


class CategoriesForm(forms.Form):
    category = forms.ModelChoiceField(label='Категория', queryset=Category.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control js-example-basic-single'}))
