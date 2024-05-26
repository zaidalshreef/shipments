from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


def send_shipment_email(shipment_data, status):
    """
    Sends an email notification about the shipment status.

    Args:
    shipment_data (dict): The JSON data containing the shipment details.
    status (str): The status of the shipment.

    Returns:
    None
    """
    domain = settings.ALLOWED_HOSTS[0]
    details_url = f"https://{domain}{reverse('shipments:shipment_detail', args=[shipment_data['shipment_id']])}"

    context = {
        'shipment_id': shipment_data['shipment_id'],
        'status': status,
        'details_url': details_url,
        'ship_from': shipment_data['ship_from'],
        'ship_to': shipment_data['ship_to'],
        'origin_lat': shipment_data['ship_from']['latitude'],
        'origin_lng': shipment_data['ship_from']['longitude'],
        'destination_lat': shipment_data['ship_to']['latitude'],
        'destination_lng': shipment_data['ship_to']['longitude'],
    }

    subject = f"Shipment {status.capitalize()} - {shipment_data['shipment_id']}"
    html_message = render_to_string('shipment_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = settings.INTERNAL_STAFF_EMAILS  # A list of internal staff emails

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
