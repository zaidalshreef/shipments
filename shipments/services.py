import requests
import json
import uuid
import pytz
from datetime import datetime
from pprint import pprint
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Shipment, ShipmentStatus, MerchantToken
from django.core.exceptions import ObjectDoesNotExist


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
            event_type = data.get('event')

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if not shipment_data:
            return JsonResponse({'error': 'Missing data in shipment_data'}, status=400)

        if event_type == 'shipment.creating':
            return handle_shipment_creation_or_update(shipment_data, status)
        elif event_type == 'shipment.cancelled':
            return handle_status_update(shipment_data.get('shipment_id'), status)
        else:
            return JsonResponse({'error': 'Unknown event type'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def handle_store_authorize(data):
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
    installation_data = data.get('data')
    # Perform any necessary actions with the installation data
    return JsonResponse({'message': f'App installed for merchant id {merchant_id}'}, status=200)


def parse_shipment_data(data):
    created_at_str = data.get('created_at')
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
    new_shipment = Shipment(**shipment_data)
    new_shipment.save()
    handle_status_update(new_shipment.shipment_id, status)
    update_salla_api(new_shipment, status)


def handle_status_update(shipment_id, status):
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
    existing_shipment = Shipment.objects.filter(shipment_id=shipment_data.get('shipment_id')).first()
    if existing_shipment:
        if shipment_data.get('type') == 'return':
            return handle_shipment_update(shipment_data)
        return handle_status_update(shipment_data.get('shipment_id'), status)
    else:
        return handle_shipment_creation(shipment_data, status)


def handle_shipment_creation(shipment_data, status):
    required_fields = ['event', 'merchant', 'created_at', 'shipment_id']
    if not all(field in shipment_data for field in required_fields):
        return JsonResponse({'error': 'Invalid shipment data provided'}, status=400)
    save_to_database(shipment_data, status)
    return JsonResponse({'message': 'Shipment creation event processed'})


def handle_shipment_update(shipment_data):
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
    shipment_id = shipment_data.get('shipment_id')
    try:
        shipment = Shipment.objects.get(shipment_id=shipment_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': "Shipment with shipment_id {} does not exist.".format(shipment_id)}, status=400)

    for key, value in shipment_data.items():
        setattr(shipment, key, value)
    shipment.save()


def update_salla_api(shipment, status):
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
    try:
        merchant_token = MerchantToken.objects.get(merchant_id=merchant_id)
        if merchant_token.is_expired():
            refresh_token(merchant_token)
        return merchant_token.access_token
    except MerchantToken.DoesNotExist:
        return None
