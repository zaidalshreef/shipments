import requests
from datetime import datetime
from django.conf import settings
from ..models import MerchantToken
from django.http import JsonResponse
import pytz
import logging

logger = logging.getLogger(__name__)


def handle_store_authorize(data):
    """
    Handles the authorization of an app being added to a store for a merchant.

    Args:
    data (dict): The data containing the merchant ID, access token, refresh token, and expires timestamp.

    Returns:
    JsonResponse: A JSON response indicating the success or failure of the authorization process.

    Raises:
    Exception: If an error occurs during the authorization process.

    Example:
    {
        "merchant": 123,
        "data": {
            "access_token": "abc123",
            "refresh_token": "def456",
            "expires": 1609459200
        }
    }
    """
    try:
        merchant_id = data.get('merchant')
        access_token = data['data'].get('access_token')
        refresh_tokens = data['data'].get('refresh_token')
        expires_at = datetime.fromtimestamp(data['data'].get('expires'))
        expires_at = pytz.utc.localize(expires_at)  # Make datetime timezone-aware
        MerchantToken.objects.update_or_create(
            merchant_id=merchant_id,
            defaults={
                'access_token': access_token,
                'refresh_token': refresh_tokens,
                'expires_at': expires_at
            }
        )
        logger.info(f"App added to store for merchant id {merchant_id}")
        return JsonResponse({'message': f'App added to store for merchant id {merchant_id}'}, status=201)
    except Exception as e:
        logger.error(f"Error handling store authorization: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def handle_app_installed(data):
    """
    Handles the installation of an app for a merchant.

    Args:
    data (dict): The data containing the merchant ID.

    Returns:
    JsonResponse: A JSON response indicating the success or failure of the installation process.

    Raises:
    Exception: If an error occurs during the installation process.

    Example:
    {
        "merchant": 123
    }
    """
    try:
        merchant_id = data.get('merchant')
        logger.info(f"App installed for merchant id {merchant_id}")
        return JsonResponse({'message': f'App installed for merchant id {merchant_id}'}, status=200)
    except Exception as e:
        logger.error(f"Error handling app installation: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def handle_app_uninstalled(data):
    """
    Handles the uninstallation of an app for a merchant.

    Args:
    data (dict): The data containing the merchant ID.

    Returns:
    JsonResponse: A JSON response indicating the success or failure of the uninstallation process.

    Raises:
    Exception: If an error occurs during the uninstallation process.

    Example:
    {
        "merchant": 123
    }
    """
    merchant_id = data.get('merchant')
    if not merchant_id:
        return JsonResponse({'error': 'Merchant ID not provided'}, status=400)

    try:
        merchant = MerchantToken.objects.filter(merchant_id=merchant_id)
        logger.info(f"App uninstalled for merchant id {merchant_id}")
        return JsonResponse({'message': f'App uninstalled for merchant id {merchant_id}'}, status=200)
    except MerchantToken.DoesNotExist:
        return JsonResponse({'error': f'MerchantToken with merchant id {merchant_id} does not exist'}, status=404)
    except Exception as e:
        logger.error(f"Error handling app uninstallation: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def refresh_token(merchant_token):
    """
    Refreshes the access token for the given merchant token.

    Args:
    merchant_token (MerchantToken): The merchant token object to refresh the access token for.

    Returns:
    bool: Returns True if the token was successfully refreshed, False otherwise.

    Raises:
    Exception: If an error occurs during the token refresh process.

    Example:
    ```
    merchant_token = MerchantToken.objects.get(pk=1)
    if refresh_token(merchant_token):
        print("Token refreshed successfully")
    else:
        print("Failed to refresh token")
    ```

    The function sends a POST request to the token refresh endpoint with the refresh token, client ID, and client secret as payload. If the response status code is 200, it extracts the new access token and expires timestamp from the JSON response and updates the merchant token object in the database. If the refresh is successful, the function returns True; otherwise, it returns False. If an error occurs during the token refresh process, the function raises an Exception.

    Note: This function assumes that the 'requests' library is imported and that the 'settings' module contains the necessary API keys and secrets.
    """
    try:
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
            logger.info(f"Token refreshed for merchant id {merchant_token.merchant_id}")
            return True
        logger.error(f"Failed to refresh token: {response.content}")
        return False
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return False


def get_access_token(merchant_id):
    """
    Retrieves the access token for the given merchant ID.

    Args:
    merchant_id (int): The ID of the merchant for which the access token is being retrieved.

    Returns:
    str: The access token for the specified merchant, or None if the token could not be retrieved.

    Raises:
    Exception: If an error occurs during the token retrieval process.

    Example:
    ```
    token = get_access_token(123)
    if token:
        print("Access token retrieved successfully")
    else:
        print("Failed to retrieve access token")
    ```

    The function first attempts to retrieve the merchant token object from the database using the provided merchant ID. If the token is expired, it attempts to refresh the token using the `refresh_token` function. If the token retrieval or refresh is successful, the function returns the access token; otherwise, it returns None. If an error occurs during the token retrieval process, the function raises an Exception.

    Note: This function assumes that the 'requests' library is imported and that the 'settings' module contains the necessary API keys and secrets.
    """
    try:
        merchant_token = MerchantToken.objects.get(merchant_id=merchant_id)
        if merchant_token.is_expired():
            if not refresh_token(merchant_token):
                return None
        return merchant_token.access_token
    except MerchantToken.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error getting access token: {str(e)}")
        return None


def update_salla_api(shipment, status):
    """
    Updates the Salla API for a given shipment with the specified status.

    Args:
    shipment (Shipment): The shipment object for which the Salla API should be updated.
    status (str): The new status of the shipment.

    Returns:
    None: This function does not return any value.

    Raises:
    Exception: If an error occurs during the update process.

    Example:
    ```
    # Assuming shipment is an instance of the Shipment model
    update_salla_api(shipment, 'created')
    ```

    This function updates the Salla API for a given shipment with the specified status. It first retrieves the access token for the shipment's merchant using the `get_access_token` function. If the token retrieval is successful, it constructs the API URL and payload for the PUT request, including the shipment ID, status, and optional PDF label and cost. The function then sends the request to the Salla API and logs any errors that occur during the process. If the request is successful, the function logs an informational message indicating that the Salla API has been updated.

    Note: This function assumes that the 'requests' library is imported and that the 'settings' module contains the necessary API keys and secrets.
    """
    try:
        logger.info(f"Updating Salla API for shipment {shipment.shipment_id} status {status}")
        token = get_access_token(shipment.merchant)
        if not token:
            logger.error("Unable to retrieve access token")
            return

        shipment_id = shipment.shipment_id
        api_url = f'https://api.salla.dev/admin/v2/shipments/{shipment_id}'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        if status == 'created':
            payload = {
                'shipment_number': str(shipment.shipping_number),
                'status': status,
                'pdf_label': shipment.label.get('url', '') if shipment.label else '',
                'cost': 19
            }
        else:
            payload = {
                'shipment_number': str(shipment.shipping_number),
                'status': status
            }
        response = requests.put(api_url, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to update Salla API: {response.content}")
    except Exception as e:
        logger.error(f"Error updating Salla API: {str(e)}")
