from django.urls import path
from .views import *

app_name = 'cart'

urlpatterns = [
    path('', CartDetailView.as_view(), name='cart_detail_url'),
    path('add/<int:product_id>/', CartAddProductFormView.as_view(), name='cart_add_url'),
    path('remove/<int:product_id>/', cart_remove, name='cart_remove_url')
    ]

