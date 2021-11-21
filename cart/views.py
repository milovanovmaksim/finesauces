from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views.generic import View
from django.urls import reverse_lazy

from .forms import CartAddProductForm
from listings.models import Product


def get_cart(request):
    cart = request.session.get(settings.CART_ID)
    if not cart:
        cart = request.session[settings.CART_ID] = {}
    return cart


def cart_clear(request):
    del request.session[settings.CART_ID]


class CartAddProductFormView(View):
    class_form = CartAddProductForm
    cart = None
    product = None
    product_id = None
    category_slug = None
    product_slug = None

    def post(self, request, *args,  **kwargs):

        form = self.class_form(request.POST)
        if form.is_valid():
            return self.form_valid(form)
            
        return redirect('listings:product_detail',
                        category_slug=self.category_slug,
                        product_slug=self.product_slug)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = get_cart(self.request)
        self.product = get_object_or_404(Product, id=self.kwargs.get('product_id'))
        self.product_id = str(self.product.id)
        self.category_slug = self.product.category.slug
        self.product_slug = self.product.slug

    def form_valid(self, form):
        data = form.cleaned_data
        if self.product_id not in self.cart:
            self.cart[self.product_id] = {
                'quantity': 0,
                'price': str(self.product.price)}
        if self.request.POST.get('overwrite_qty'):
            self.cart[self.product_id]['quantity'] = data['quantity']
        else:
            self.cart[self.product_id]['quantity'] += data['quantity']
        self.request.session.modified = True
        return redirect(reverse_lazy('cart:cart_detail_url'))


class CartDetailView(View):
    template_name = 'cart/cart_detail.html'
    cart = None
    product_ids = None
    products = None
    temp_cart = None

    def get(self, request, *args,  **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = get_cart(request)
        self.product_ids = self.cart.keys()
        self.products = Product.objects.filter(id__in=self.product_ids)
        self.temp_cart = self.cart.copy()

    def get_context_data(self):
        for product in self.products:
            cart_item = self.temp_cart[str(product.id)]
            #cart_item['price'] = product.price
            cart_item['product'] = product
            cart_item['total_price'] = (Decimal(cart_item['price']) * cart_item['quantity'])
            cart_item['update_quantity_form'] = CartAddProductForm(initial={
                'quantity': cart_item['quantity']
            })
        cart_total_price = sum(Decimal(item['price']) * item['quantity'] for item in self.temp_cart.values())
        context = {'cart': self.temp_cart.values(),
                   'cart_total_price': cart_total_price}
        return context


def cart_remove(request, product_id):
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session.modified = True
        return redirect('cart:cart_detail_url')

