import requests
import json
import uuid
import pytz
from datetime import datetime
from pprint import pprint
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from .models import Shipment, ShipmentStatus, MerchantToken
from django.utils.html import strip_tags
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


@csrf_exempt
def webhook_handler(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pprint(data)

            if data.get('event') == 'app.store.authorize':
                return handle_store_authorize(data)

            if data.get('event') == 'app.installed':
                return handle_app_installed(data)

            shipment_data, status = parse_shipment_data(data)
            if status == 'creating':
                status = 'created'
            event_type = data.get('event')

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if not shipment_data:
            return JsonResponse({'error': 'Missing data in shipment_data'}, status=400)

        if event_type == 'shipment.creating':
            response = handle_shipment_creation_or_update(shipment_data, status)
            send_shipment_email(shipment_data, 'created')
            return response
        elif event_type == 'shipment.cancelled':
            response = handle_status_update(shipment_data.get('shipment_id'), status)
            send_shipment_email(shipment_data, 'cancelled')
            return response
        else:
            return JsonResponse({'error': 'Unknown event type'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def generate_pdf_label(request, shipment_id):
    # Fetch shipment details from the database
    shipment = Shipment.objects.get(id=shipment_id)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="shipment_label_{shipment_id}.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Draw the shipment details on the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Shipment Label")

    # Sender's Information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 100, "Sender's Information")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 120, f"Name: {shipment.ship_from['name']}")
    p.drawString(100, height - 140, f"Address: {shipment.ship_from['address_line']}")
    p.drawString(100, height - 160, f"City: {shipment.ship_from['city']}")
    p.drawString(100, height - 180, f"Country: {shipment.ship_from['country']}")
    p.drawString(100, height - 200, f"Phone: {shipment.ship_from['phone']}")
    p.drawString(100, height - 220, f"Email: {shipment.ship_from['email']}")

    # Recipient's Information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 260, "Recipient's Information")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 280, f"Name: {shipment.ship_to['name']}")
    p.drawString(100, height - 300, f"Address: {shipment.ship_to['address_line']}")
    p.drawString(100, height - 320, f"City: {shipment.ship_to['city']}")
    p.drawString(100, height - 340, f"Country: {shipment.ship_to['country']}")
    p.drawString(100, height - 360, f"Phone: {shipment.ship_to['phone']}")
    p.drawString(100, height - 380, f"Email: {shipment.ship_to['email']}")

    # Shipment Details
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 420, "Shipment Details")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 440, f"Tracking Number: {shipment.tracking_number}")
    p.drawString(100, height - 460, f"Tracking Link: {shipment.tracking_link}")
    p.drawString(100, height - 480, f"Total Weight: {shipment.total_weight['value']} {shipment.total_weight['units']}")
    p.drawString(100, height - 500, f"Total Cost: {shipment.total['amount']} {shipment.total['currency']}")

    # Shipping Cost
    p.drawString(100, height - 540, "Shipping Cost: 19 SAR")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    return response


def send_shipment_email(shipment_data, status):
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


def handle_store_authorize(data):
    """
    Handles the event of an app being added to a store for a specific merchant.

    Args:
    data (dict): The JSON data containing the event details.

    Returns:
    JsonResponse: A JSON response indicating the success of adding the app to the store.

    Raises:
    ValueError: If the 'merchant' field is missing in the data.

    """
    merchant_id = data.get('merchant')
    access_token = data['data'].get('access_token')
    refresh_tokens = data['data'].get('refresh_token')
    expires_at = datetime.fromtimestamp(data['data'].get('expires'))
    expires_at = pytz.utc.localize(expires_at)  # Make datetime timezone-aware
    MerchantToken.objects.create(
        merchant_id=merchant_id,
        access_token=access_token,
        refresh_token=refresh_tokens,
        expires_at=expires_at
    )
    return JsonResponse({'message': f'App added to store for merchant id {merchant_id}'}, status=201)


def handle_app_installed(data):
    # Handle app installation event here
    merchant_id = data.get('merchant')
    # Perform any necessary actions with the installation data
    return JsonResponse({'message': f'App installed for merchant id {merchant_id}'}, status=200)


def parse_shipment_data(data):
    """
    Parses the shipment data from the incoming JSON payload.

    Args:
    data (dict): The JSON data containing the shipment details.

    Returns:
    tuple: A tuple containing the parsed shipment data and its status.

    Raises:
    ValueError: If the 'created_at' field is missing in the data.

    """
    created_at_str = data.get('created_at')
    if not created_at_str:
        raise ValueError("Missing 'created_at' field in the shipment data")

    created_at = datetime.strptime(created_at_str, '%a %b %d %Y %H:%M:%S GMT%z')
    created_at_str = created_at.isoformat()

    status = data['data'].get('status')

    shipment_data = {
        'event': data.get('event'),
        'merchant': data.get('merchant'),
        'created_at': created_at_str,
        'shipment_id': data['data'].get('id'),
        'type': data['data'].get('type'),
        'courier_name': data['data'].get('courier_name'),
        'courier_logo': data['data'].get('courier_logo'),
        'tracking_number': data['data'].get('tracking_number'),
        'tracking_link': data['data'].get('tracking_link'),
        'payment_method': data['data'].get('payment_method'),
        'total': data['data'].get('total'),
        'cash_on_delivery': data['data'].get('cash_on_delivery'),
        'label': data['data'].get('label'),
        'total_weight': data['data'].get('total_weight'),
        'created_at_details': data['data'].get('created_at'),
        'packages': data['data'].get('packages'),
        'ship_from': data['data'].get('ship_from'),
        'ship_to': data['data'].get('ship_to'),
        'meta': data['data'].get('meta'),
    }

    return shipment_data, status


def save_to_database(shipment_data, status):
    """
    Saves the shipment data to the database and then updates the shipment status.

    Args:
    shipment_data (dict): The shipment data to be saved.
    status (str): The status of the shipment.

    Returns:
    Shipment: The created shipment object.

    Raises:
    ValueError: If the shipment data is missing any required fields.

    """

    new_shipment = Shipment(**shipment_data)  # Create a new Shipment object from the shipment data
    new_shipment.save()  # Save the Shipment object to the database
    handle_status_update(new_shipment.shipment_id, status)  # Update the shipment status
    return new_shipment


def handle_status_update(shipment_id, status):
    """
    Updates the status of a shipment in the database and triggers an update to the Salla API.

    Args:
    shipment_id (str): The unique identifier of the shipment.
    status (str): The new status of the shipment.

    Returns:
    JsonResponse: A JSON response indicating the success of updating the shipment status.

    Raises:
    Shipment.DoesNotExist: If the shipment with the given shipment_id does not exist in the database.

    """
    try:
        shipment = Shipment.objects.get(shipment_id=shipment_id)
    except Shipment.DoesNotExist:
        return JsonResponse({'error': 'Shipment not found'}, status=404)

    new_status = ShipmentStatus(
        shipment=shipment,
        status=status
    )
    new_status.save()
    if status != 'cancelled':
        update_salla_api(shipment, status)
    return JsonResponse({'message': 'Shipment status updated successfully'}, status=200)


def handle_shipment_creation_or_update(shipment_data, status):
    """
    Handles the event of a shipment creation or update.

    Args:
    shipment_data (dict): The JSON data containing the shipment details.
    status (str): The status of the shipment.

    Returns:
    JsonResponse: A JSON response indicating the success of processing the shipment event.

    Raises:
    ValueError: If the shipment data is missing any required fields.
    Shipment.DoesNotExist: If the shipment with the given shipment_id does not exist in the database.

    """
    existing_shipment = Shipment.objects.filter(shipment_id=shipment_data.get('shipment_id')).first()
    if existing_shipment and shipment_data.get('type') == 'return':
        handle_shipment_update(shipment_data)
        return handle_status_update(shipment_data.get('shipment_id'), 'created')
    elif existing_shipment:
        return handle_status_update(shipment_data.get('shipment_id'), status)
    else:
        shipment = handle_shipment_creation(shipment_data, status)
        pdf_label_url = request.build_absolute_uri(reverse('generate_pdf_label', args=[shipment.shipment_id]))
        shipment['label'] = {'url': pdf_label_url}
        shipment.save()
        return JsonResponse({'message': 'Shipment creation event processed', 'pdf_label': pdf_label_url})


def handle_shipment_creation(shipment_data, status):
    """
    Handles the event of a shipment creation.

    Args:
    shipment_data (dict): The JSON data containing the shipment details.
    status (str): The status of the shipment.

    Returns:
    Shipment: The created shipment object.

    Raises:
    ValueError: If the shipment data is missing any required fields.
    Shipment.DoesNotExist: If the shipment with the given shipment_id does not exist in the database.

    """
    required_fields = ['event', 'merchant', 'created_at', 'shipment_id']
    if not all(field in shipment_data for field in required_fields):
        return JsonResponse({'error': 'Invalid shipment data provided'}, status=400)

    shipment = save_to_database(shipment_data, status)
    return shipment


def handle_shipment_update(shipment_data):
    """
    Handles the event of a shipment update.

    Args:
    shipment_data (dict): The JSON data containing the shipment details.

    Returns:
    JsonResponse: A JSON response indicating the success of processing the shipment update event.

    Raises:
    ValueError: If the shipment data is missing any required fields.
    Shipment.DoesNotExist: If the shipment with the given shipment_id does not exist in the database.

    """
    if shipment_data is None:
        return JsonResponse({'error': 'No shipment data provided'}, status=400)

    shipment_id = shipment_data.get('shipment_id')
    if shipment_id is None:
        return JsonResponse({'error': 'Missing shipping id in payload'}, status=400)

    update_database(shipment_data)
    return JsonResponse({'message': 'Shipment update event processed'}, status=200)


def update_database(shipment_data):
    """
    Updates the shipment data in the database.

    Args:
    shipment_data (dict): The JSON data containing the updated shipment details.

    Returns:
    None: This function does not return any value. It updates the shipment data in the database.

    Raises:
    ObjectDoesNotExist: If the shipment with the given shipment_id does not exist in the database.

    """
    shipment_id = shipment_data.get('shipment_id')
    try:
        shipment = Shipment.objects.get(shipment_id=shipment_id)
    except Shipment.DoesNotExist:
        return JsonResponse({'error': "Shipment with shipment_id {} does not exist.".format(shipment_id)}, status=400)

    for key, value in shipment_data.items():
        setattr(shipment, key, value)
    shipment.save()


def update_salla_api(shipment, status):
    """
    Updates the shipment details in the Salla API.

    Args:
    shipment (Shipment): The shipment object containing the updated shipment details.
    status (str): The new status of the shipment.

    Returns:
    None: This function does not return any value. It updates the shipment details in the Salla API.

    Raises:
    ValueError: If the shipment data is missing any required fields.
    Shipment.DoesNotExist: If the shipment with the given shipment_id does not exist in the database.

    """
    print(f"Updating Salla API for shipment {shipment.shipment_id} status  {status}")
    token = get_access_token(shipment.merchant)
    shipment_id = shipment.shipment_id
    api_url = f'https://api.salla.dev/admin/v2/shipments/{shipment_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'shipment_number': str(shipment.shipping_number),  # Convert UUID to string
        'status': status,
        'pdf_label': shipment.label.get('url', '') if shipment.label else '',
        'cost': 19  # Update the cost based on the shipment details
    }
    response = requests.put(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to update Salla API: {response.content}")


def refresh_token(merchant_token):
    """
    Refreshes the access token for a given merchant token.

    Args:
    merchant_token (MerchantToken): The merchant token object containing the refresh token.

    Returns:
    bool: Returns True if the token refresh was successful, False otherwise.

    Raises:
    ValueError: If the merchant token does not exist.

    This function sends a POST request to the Salla API's token endpoint with the refresh token, client ID, and client secret.
    If the response status code is 200, it extracts the new access token and expires time from the JSON response and updates the merchant token object in the database.
    """
    refresh_url = 'https://accounts.salla.sa/oauth2/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': merchant_token.refresh_token,
        'client_id': settings.SALLA_API_KEY,
        'client_secret': settings.SALLA_API_SECRET,
    }
    response = requests.post(refresh_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        merchant_token.access_token = token_data.get('access_token')
        expires_in = token_data.get('expires')
        merchant_token.expires_at = datetime.fromtimestamp(expires_in)
        merchant_token.save()
        return True
    return False


def get_access_token(merchant_id):
    """
    Retrieves the access token for the given merchant ID from the database.
    If the token is expired, it refreshes the token using the refresh token.

    Args:
    merchant_id (str): The unique identifier of the merchant.

    Returns:
    str: The access token for the given merchant ID. If the token does not exist or is expired, returns None.

    Raises:
    MerchantToken.DoesNotExist: If the merchant token with the given merchant ID does not exist in the database.

    This function first attempts to retrieve the merchant token object from the database using the provided merchant ID.
    If the token is expired (i.e., its expiration time has passed), it refreshes the token by sending a POST request to the Salla API's token endpoint with the refresh token, client ID, and client secret.
    If the response status code is 200, it extracts the new access token and expires time from the JSON response and updates the merchant token object in the database.
    Finally, it returns the access token for the given merchant ID.
    """
    try:
        merchant_token = MerchantToken.objects.get(merchant_id=merchant_id)
        if merchant_token.is_expired():
            refresh_token(merchant_token)
        return merchant_token.access_token
    except MerchantToken.DoesNotExist:
        return None
