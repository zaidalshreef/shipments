import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# from twilio.rest import Client

logger = logging.getLogger(__name__)


# twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def send_shipment_email(shipment, status):
    """
    Sends an email to internal staff about a shipment with a specified status.

    Args:
    shipment (Shipment): The shipment object containing details about the shipment.
    status (str): The status of the shipment, such as "shipped", "delivered", etc.

    Returns:
    None

    Raises:
    Exception: If an error occurs while sending the email.

    Example:
    >>> from .models import Shipment
    >>> shipment = Shipment.objects.get(shipment_id=123)
    >>> send_shipment_email(shipment, "shipped")
    """
    logger.info(f"Sending email for shipment {shipment.shipment_id} with status {status}")
    try:
        subject = f"Shipment {status.capitalize()} - {shipment.shipping_number}"
        context = {
            'type': shipment.type,
            'shipping_number': shipment.shipping_number,
            'status': status,
            'details_url': f"https://{settings.ALLOWED_HOSTS[0]}/shipments/{shipment.shipment_id}",
            'ship_from': shipment.ship_from,
            'ship_to': shipment.ship_to,
        }
        html_message = render_to_string('shipment_email.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = settings.INTERNAL_STAFF_EMAILS  # List of internal staff emails

        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        logger.info(f"Email sent successfully for shipment {shipment.shipment_id} with status {status}")
    except Exception as e:
        logger.error(f"Failed to send email for shipment {shipment.shipment_id} with status {status}: {str(e)}")

# def send_sms(shipment):
#     try:
#         message = f"شحنة {shipment.shipping_number} من {shipment.ship_from['name']} في الطريق الآن."
#         twilio_client.messages.create(
#             body=message,
#             from_=settings.TWILIO_PHONE_NUMBER,
#             to=str(+966507368133)
#         )
#         logger.info(f"SMS sent to {shipment.ship_to['phone']}")
#     except Exception as e:
#         logger.error(f"Error sending SMS: {str(e)}")
#
#
# def send_whatsapp(shipment):
#     try:
#         message = f"شحنة {shipment.shipping_number} من {shipment.ship_from['name']} في الطريق الآن."
#         twilio_client.messages.create(
#             body=message,
#             from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,
#             to='whatsapp:' + shipment.ship_to['phone']
#         )
#         logger.info(f"WhatsApp message sent to {shipment.ship_to['phone']}")
#     except Exception as e:
#         logger.error(f"Error sending WhatsApp message: {str(e)}")
