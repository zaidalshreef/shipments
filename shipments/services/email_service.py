from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from asgiref.sync import sync_to_async


def send_shipment_email(shipment_data, status):
    subject = f"Shipment {status.capitalize()} - {shipment_data['shipment_id']}"
    context = {
        'type': shipment_data['type'],
        'shipment_id': shipment_data['shipment_id'],
        'status': status,
        'details_url': f"https://{settings.ALLOWED_HOSTS[0]}/shipments/{shipment_data['shipment_id']}",
        'ship_from': shipment_data['ship_from'],
        'ship_to': shipment_data['ship_to'],
    }
    html_message = render_to_string('shipment_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.INTERNAL_STAFF_EMAILS  # List of internal staff emails

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
