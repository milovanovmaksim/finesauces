from decimal import Decimal

from cart.views import get_cart


def cart(request):
    cart = get_cart(request)
    cart_total_price = sum(Decimal(item['price']) *
                            Decimal(item['quantity']) for item in cart.values())
    return { 'cart_total_price': cart_total_price }