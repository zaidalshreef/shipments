import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_shipment_email(shipment_data, status):
    try:
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
        logger.info(f"Email sent successfully for shipment {shipment_data['shipment_id']} with status {status}")
    except Exception as e:
        logger.error(f"Failed to send email for shipment {shipment_data['shipment_id']} with status {status}: {str(e)}")
