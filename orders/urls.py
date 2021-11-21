from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required

from .views import *
from decorators import user_created_order

app_name = 'orders'

urlpatterns = [
    path('create/', OrderCreateViewForm.as_view(), name='order_create_url'),
    path('admin/order/<int:order_id>/pdf/', staff_member_required(invoice_pdf), name='invoice_pdf_url'),
    path('order/<int:order_id>/pdf/', user_created_order(customer_invoice_pdf), name='customer_invoice_pdf'),
    path('order/<int:order_id>/', OrderDetailView.as_view(), name='order_detail_url')
]
