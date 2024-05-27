import requests
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from ..models import MerchantToken
import pytz
from asgiref.sync import sync_to_async
import httpx


async def handle_store_authorize(data):
    merchant_id = data.get('merchant')
    access_token = data['data'].get('access_token')
    refresh_tokens = data['data'].get('refresh_token')
    expires_at = datetime.fromtimestamp(data['data'].get('expires'))
    expires_at = pytz.utc.localize(expires_at)  # Make datetime timezone-aware

    await sync_to_async(MerchantToken.objects.update_or_create)(
        merchant_id=merchant_id,
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_tokens,
            'expires_at': expires_at
        }
    )

    return JsonResponse({'message': f'App added to store for merchant id {merchant_id}'}, status=201)


async def handle_app_installed(data):
    merchant_id = data.get('merchant')
    return JsonResponse({'message': f'App installed for merchant id {merchant_id}'}, status=200)


async def handle_app_uninstalled(data):
    merchant_id = data.get('merchant')
    if not merchant_id:
        return JsonResponse({'error': 'Merchant ID not provided'}, status=400)

    try:
        merchant_token = await sync_to_async(MerchantToken.objects.get)(merchant_id=merchant_id)
        await sync_to_async(merchant_token.delete)()
        return JsonResponse({'message': f'App uninstalled for merchant id {merchant_id}'}, status=200)
    except MerchantToken.DoesNotExist:
        return JsonResponse({'error': f'MerchantToken with merchant id {merchant_id} does not exist'}, status=404)


async def refresh_token(merchant_token):
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
        await sync_to_async(merchant_token.save)()
        return True
    return False


async def get_access_token(merchant_id):
    try:
        merchant_token = await sync_to_async(MerchantToken.objects.get)(merchant_id=merchant_id)
        if merchant_token.is_expired():
            await refresh_token(merchant_token)
        return merchant_token.access_token
    except MerchantToken.DoesNotExist:
        return None


async def update_salla_api(shipment, status):
    print(f"Updating Salla API for shipment {shipment.shipment_id} status {status}")
    token = await get_access_token(shipment.merchant)
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
    async with httpx.AsyncClient() as client:
        response = await client.put(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to update Salla API: {response.content}")
