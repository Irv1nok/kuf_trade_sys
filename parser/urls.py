from django.urls import path

from parser.views import index, parse_pages, SearchItemsList, ItemDetailView


urlpatterns = [
    path('', index, name='home'),
    path('parser/', parse_pages, name='parse_pages'),
    path('list/', SearchItemsList.as_view(), name='search_items_list'),
    path('item-detail/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
]
