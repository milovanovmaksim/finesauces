from django.shortcuts import redirect

from orders.models import Order


def user_created_order(view_func):
    def wrap(request, *args, **kwargs):
        order_id = kwargs['order_id']
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return redirect('profile_url')
        return view_func(request, *args, **kwargs)
    return wrap