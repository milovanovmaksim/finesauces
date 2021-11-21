from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View

from .models import Category, Product, Review
from .forms import ReviewForm
from cart.forms import CartAddProductForm


class ProductListView(View):
    template_name = 'listings/product/product_list.html'
    objects_name = 'products'
    model = Product

    def get(self, request, *args,  **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_queryset(self):
        self.requested_category = None
        if self.kwargs.get('category_slug'):
            self.requested_category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
            return self.model.objects.get_by_category(category=self.requested_category)
        return self.model.objects.all()

    def get_context_data(self):
        categories = Category.objects.all()
        context = {self.objects_name: self.get_queryset(),
                   'categories': categories,
                   'requested_category': self.requested_category}
        return context


class ProductDetailView(View):
    template_name = 'listings/product/product_detail.html'
    object_name = 'product'
    model = Product
    slug_url_kwarg = 'product_slug'

    def get(self, request, *args,  **kwargs):
        review_form = ReviewForm()
        cart_product_form = CartAddProductForm()
        return render(request, self.template_name,
                      context=self.get_context_data(review_form=review_form,
                                                    cart_product_form=cart_product_form))

    def post(self, request, *args,  **kwargs):
        review_form = ReviewForm(request.POST)
        cart_product_form = CartAddProductForm(request.POST)
        product = self.get_object()
        if review_form.is_valid():
            data = review_form.cleaned_data
            author_name = "Anonymous"
            if request.user.is_authenticated and request.user.first_name != '':
                author_name = f"{request.user.first_name} {request.user.last_name}"
            Review.objects.create(
                product=product,
                author=author_name,
                rating=data['rating'],
                text=data['text'])
            return redirect('listings:product_detail',
                            category_slug=self.category_slug,
                            product_slug=self.product_slug)
        return render(request, self.template_name,
                      context=self.get_context_data(review_form=review_form,
                                                    cart_product_form=cart_product_form))

    def get_object(self):
        self.category_slug = self.kwargs.get('category_slug')
        self.product_slug = self.kwargs.get(self.slug_url_kwarg)
        return Product.objects.get_by_slug(product_slug=self.product_slug, category_slug=self.category_slug)

    def get_context_data(self, **kwargs):
        review_form = kwargs.get('review_form')
        cart_product_form = kwargs.get('cart_product_form')
        context = {self.object_name: self.get_object(),
                   'review_form': review_form,
                   'cart_product_form': cart_product_form}
        return context
