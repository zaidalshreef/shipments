import pytest
import json
from django.urls import reverse
from django.http import JsonResponse
from unittest.mock import patch, Mock, MagicMock
from shipments.services.webhook_service import webhook_handler
from django.test import Client, RequestFactory


@pytest.mark.django_db
@patch('shipments.services.webhook_service.handle_store_authorize')
@patch('shipments.services.webhook_service.handle_app_installed')
@patch('shipments.services.webhook_service.handle_app_uninstalled')
@patch('shipments.services.webhook_service.handle_shipment_creation_or_update')
@patch('shipments.services.webhook_service.parse_shipment_data')
def test_webhook_handler_valid_events(mock_parse_shipment_data, mock_handle_shipment_creation_or_update,
                                      mock_handle_app_uninstalled, mock_handle_app_installed,
                                      mock_handle_store_authorize, rf):
    url = reverse('shipments:shipment_webhook')
    data_store_authorize = json.dumps({"event": "app.store.authorize", "merchant": 123,
                                       "data": {"access_token": "abc123", "refresh_token": "def456",
                                                "expires": 1609459200}})
    data_app_installed = json.dumps({"event": "app.installed", "merchant": 123})
    data_app_uninstalled = json.dumps({"event": "app.uninstalled", "merchant": 123})
    data_shipment_creating = json.dumps(
        {"event": "shipment.creating", "created_at": "2023-01-01T00:00:00Z",  # Corrected format
         "data": {"id": 1, "status": "created"}})
    data_shipment_cancelled = json.dumps(
        {"event": "shipment.cancelled", "created_at": "2023-01-01T00:00:00Z",  # Corrected format
         "data": {"id": 1, "status": "cancelled"}})

    request_store_authorize = rf.post(url, data_store_authorize, content_type='application/json')
    request_app_installed = rf.post(url, data_app_installed, content_type='application/json')
    request_app_uninstalled = rf.post(url, data_app_uninstalled, content_type='application/json')
    request_shipment_creating = rf.post(url, data_shipment_creating, content_type='application/json')
    request_shipment_cancelled = rf.post(url, data_shipment_cancelled, content_type='application/json')

    mock_parse_shipment_data.return_value = ({"shipment_id": 1}, "created")

    # Test store authorize event
    response = webhook_handler(request_store_authorize)
    print(f"Store Authorize Response: {response.content}")  # Added for debugging
    mock_handle_store_authorize.return_value = JsonResponse({'message': f'App added to store for merchant id {data_store_authorize['merchant']}'}, status=201)
    assert response.status_code == 201
    mock_handle_store_authorize.assert_called_once()

    # Test app installed event
    response = webhook_handler(request_app_installed)
    print(f"App Installed Response: {response.content}")  # Added for debugging
    assert response.status_code == 200
    mock_handle_app_installed.assert_called_once()

    # Test app uninstalled event
    response = webhook_handler(request_app_uninstalled)
    print(f"App Uninstalled Response: {response.content}")  # Added for debugging
    assert response.status_code == 200
    mock_handle_app_uninstalled.assert_called_once()

    # Test shipment creating event
    response = webhook_handler(request_shipment_creating)
    print(f"Shipment Creating Response: {response.content}")  # Added for debugging
    assert response.status_code == 201
    mock_handle_shipment_creation_or_update.assert_called_once()

    # Test shipment cancelled event
    response = webhook_handler(request_shipment_cancelled)
    print(f"Shipment Cancelled Response: {response.content}")  # Added for debugging
    assert response.status_code == 201
    mock_handle_shipment_creation_or_update.assert_called()


@pytest.mark.django_db
def test_webhook_handler_invalid_json():
    client = Client()
    response = client.post(reverse('shipments:shipment_webhook'), data="Invalid JSON", content_type="application/json")
    assert response.status_code == 400
    assert json.loads(response.content) == {'error': 'Invalid JSON data'}


@pytest.mark.django_db
def test_webhook_handler_unknown_event(mocker):
    client = Client()
    data = json.dumps({
        'event': 'shipment.unknown',
        'merchant': 123,
        'created_at': 'Wed, 13 Oct 2021 07:53:00 GMT',
        'data': {
            'id': 1,
            'status': 'creating',
            'type': 'standard',
            'courier_name': 'DHL',
            'courier_logo': 'https://example.com/logo.png',
            'tracking_number': '1234567890',
            'tracking_link': 'https://example.com/track/1234567890',
            'payment_method': 'COD',
            'total': {'amount': 100, 'currency': 'USD'},
            'cash_on_delivery': {'amount': 10, 'currency': 'USD'},
            'label': {'url': 'https://example.com/label.pdf'},
            'total_weight': {'weight': 5, 'unit': 'kg'},
            'created_at_details': 'some details',
            'packages': [{'id': 1, 'weight': 5}],
            'ship_from': {'address': '123 Street, City, Country'},
            'ship_to': {'address': '456 Avenue, City, Country'},
            'meta': {'info': 'some info'},
        }
    })
    mocker.patch('shipments.services.shipment_service.parse_shipment_data', return_value=({}, 'created'))
    response = client.post(reverse('shipments:shipment_webhook'), data=data, content_type="application/json")
    assert response.status_code == 400
    assert json.loads(response.content) == {'error': 'Unknown event type'}


@pytest.mark.django_db
def test_webhook_handler_method_not_allowed(rf):
    url = reverse('shipments:shipment_webhook')
    request = rf.get(url)

    response = webhook_handler(request)

    assert response.status_code == 405
    assert json.loads(response.content) == {'error': 'Method not allowed'}
