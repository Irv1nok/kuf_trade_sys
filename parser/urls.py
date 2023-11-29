from parser.views import about, index, parse_pages, SearchItemsList, ItemDetailView

from django.urls import path


urlpatterns = [
    path('', index, name='home'),
    path('parser/', parse_pages, name='parse_pages'),
    path('list/', SearchItemsList.as_view(), name='search_items_list'),
    path('item-detail/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('about/', about, name='about'),
]
