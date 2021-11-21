from django.urls import path
from .views import *

app_name = 'listings'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list_url'),
    path('<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', ProductDetailView.as_view(), name='product_detail')

    ]

