from io import BytesIO

from celery import shared_task

from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

import weasyprint

from .models import Order


@shared_task
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = f"Order nr. {order.id}"
    message = f"Dear {order.first_name}, \n\n" \
              f"Your order was succesfully created.\n" \
              f"Your order ID is {order.id}"
    email = EmailMessage(
        subject=subject,
        body=message,
        to=[order.email]
    )
    attached_pdf_email = attach_pdf_to_email(email, order)
    attached_pdf_email.send()


@shared_task
def status_change_notification(order_id):
    order = Order.objects.get(id=order_id)
    subject = f"Order nr. {order.id}"
    message = f"Dear {order.first_name}, \n\n"\
              f"Staus of your order {order.id} was changed to {order.status}"
    mail_sent = send_mail(subject=subject, message=message, 
                          from_email=None, recipient_list=[order.email])
    return mail_sent


def attach_pdf_to_email(email, order):
    html = render_to_string('orders/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    return email