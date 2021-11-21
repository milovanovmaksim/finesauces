from django.views.generic import View
from django.shortcuts import redirect

from .models import Order

class UserCreatedOrderMixin(View):
    order = None
    
    def dispatch(self, request, *args, **kwargs):
        order_id = kwargs['order_id']
        try:
            self.order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return redirect('profile_url')
        return super().dispatch(request, *args, **kwargs)