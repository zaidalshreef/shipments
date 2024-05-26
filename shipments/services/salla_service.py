import requests
from datetime import datetime
from django.conf import settings
from ..models import MerchantToken


def handle_store_authorize(data):
    merchant_id = data.get('merchant')
    access_token = data['data'].get('access_token')
    refresh_tokens = data['data'].get('refresh_token')
    expires_at = datetime.fromtimestamp(data['data'].get('expires'))
    MerchantToken.objects.create(
        merchant_id=merchant_id,
        access_token=access_token,
        refresh_token=refresh_tokens,
        expires_at=expires_at
    )
    return JsonResponse({'message': f'App added to store for merchant id {merchant_id}'}, status=201)


def handle_app_installed(data):
    merchant_id = data.get('merchant')
    return JsonResponse({'message': f'App installed for merchant id {merchant_id}'}, status=200)


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


def update_salla_api(shipment, status):
    print(f"Updating Salla API for shipment {shipment.shipment_id} status {status}")
    token = get_access_token(shipment.merchant)
    shipment_id = shipment.shipment_id
    api_url = f'https://api.salla.dev/admin/v2/shipments/{shipment_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'shipment_number': str(shipment.shipping_number),
        'status': status,
        'pdf_label': shipment.label.get('url', '') if shipment.label else '',
        'cost': 19
    }
    response = requests.put(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to update Salla API: {response.content}")
