from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

import stripe
import weasyprint

from . forms import OrderCreateForm
from .tasks import order_created
from .models import OrderItem, Order
from cart.views import get_cart, cart_clear
from listings.models import Product
from decorators import user_created_order
from .mixins import UserCreatedOrderMixin


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class OrderCreateViewForm(View):
    class_form = OrderCreateForm
    cart = None
    cart_qty = None
    transport_cost = None
    order = None
    template_name = 'orders/order_create.html'
    successful_template_name = 'orders/order_created.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = get_cart(request)
        self.cart_qty = sum(item['quantity'] for item in self.cart.values())
        self.transport_cost = round((3.99 + (self.cart_qty // 10) * 1.5), 2)

    def post(self, request, *args, **kwargs):
        order_form = self.class_form(request.POST)
        if order_form.is_valid():
            self.form_valid(order_form)
            return render(request, self.successful_template_name, context=self.get_context_data())

    def get(self, request, *args, **kwargs):
        order_form = self.class_form()
        if request.user.is_authenticated:
            initial_data = {
                'firat_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'telephone': request.user.profile.phone_number,
                'address': request.user.profile.address,
                'postal_code': request.user.profile.postal_code,
                'city': request.user.profile.city,
                'coiuntry': request.user.profile.country
            }
            order_form = self.class_form(initial=initial_data)
        context = {
            'cart': self.cart,
            'order_form': order_form,
            'transport_cost': self.transport_cost}
        return render(request, self.template_name, context=context)

    def form_valid(self, order_form):
        data = order_form.cleaned_data
        transport = data['transport']
        if transport == "Recipient pickup":
            self.transport_cost = 0
        self.order = order_form.save(commit=False)
        if self.request.user.is_authenticated:
            self.order.user = self.request.user
        self.order.transport_cost = Decimal(self.transport_cost)
        self.order.save()

        OrderItem.objects.create_order_items(self.cart, self.order)

        self.create_charge(data)        
                
        cart_clear(self.request)
        order_created.delay(self.order.id)

    def get_context_data(self, **kwargs):
        context = {'order': self.order}
        return context
    
    def create_charge(self, data):
        customer = stripe.Customer.create(
            email=data['email'],
            source=self.request.POST['stripeToken'])

        charge = stripe.Charge.create(
            customer=customer,
            amount=int(self.order.get_total_cost() * 100),
            currency='usd',
            description=self.order)


@staff_member_required
def invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f"filename=order_{order.id}.pdf"

    html = render_to_string('orders/pdf.html', {'order':order})
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response


@user_created_order
def customer_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    
    # generate pdf
    html = render_to_string('orders/pdf.html', {'order': order})
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response


class OrderDetailView(UserCreatedOrderMixin):
    template_name = 'orders/order_detail.html'
    object_name = 'order'
    model = Order
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context_data())
    
    def get_object(self):
        return self.order
    
    def get_context_data(self, **kwargs):
        context = {self.object_name: self.get_object()} 
        return context
    