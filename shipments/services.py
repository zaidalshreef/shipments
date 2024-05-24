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


def send_shipment_email(shipment_data, event_type):
    domain = settings.ALLOWED_HOSTS[0]  # Get the first domain from ALLOWED_HOSTS
    details_url = f"https://{domain}{reverse('shipments:shipment_detail', args=[shipment_data['shipment_id']])}"
    color = 'green' if event_type == 'created' else 'red'

    context = {
        'shipment_id': shipment_data['shipment_id'],
        'event_type': event_type,
        'details_url': details_url,
        'color': color,
    }
    subject = f"Shipment {event_type.capitalize()}"
    message = render_to_string('shipment_email.html', context)
    send_mail(subject, message, 'from@example.com', ['to@example.com'], fail_silently=False)


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
    None: This function does not return any value. It saves the shipment data and updates the status.

    Raises:
    ValueError: If the shipment data is missing any required fields.

    """
    new_shipment = Shipment(**shipment_data)  # Create a new Shipment object from the shipment data
    new_shipment.save()  # Save the Shipment object to the database
    handle_status_update(new_shipment.shipment_id, status)  # Update the shipment status


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
    if existing_shipment:
        if shipment_data.get('type') == 'return':
            return handle_shipment_update(shipment_data)
        return handle_status_update(shipment_data.get('shipment_id'), status)
    else:
        return handle_shipment_creation(shipment_data, status)


def handle_shipment_creation(shipment_data, status):
    """
    Handles the event of a shipment creation.

    Args:
    shipment_data (dict): The JSON data containing the shipment details.
    status (str): The status of the shipment.

    Returns:
    JsonResponse: A JSON response indicating the success of processing the shipment creation event.

    Raises:
    ValueError: If the shipment data is missing any required fields.
    Shipment.DoesNotExist: If the shipment with the given shipment_id does not exist in the database.

    """
    required_fields = ['event', 'merchant', 'created_at', 'shipment_id']
    if not all(field in shipment_data for field in required_fields):
        return JsonResponse({'error': 'Invalid shipment data provided'}, status=400)
    save_to_database(shipment_data, status)
    return JsonResponse({'message': 'Shipment creation event processed'})


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
    shipment = Shipment.objects.get(shipment_id=shipment_id)
    status = shipment.statuses.last().status
    update_salla_api(shipment, status)
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
        'tracking_link': shipment.tracking_link,
        'tracking_number': shipment.tracking_number,
        'status': status,
        'pdf_label': shipment.label.get('url', '') if shipment.label else '',
        'cost': shipment.total.get('amount', 0)  # Assuming 'total' is a JSONField
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
