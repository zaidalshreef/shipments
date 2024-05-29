import pytest
import json
from django.urls import reverse
from django.http import JsonResponse
from unittest.mock import patch, Mock
from shipments.services.webhook_service import webhook_handler


@pytest.mark.django_db
@patch('shipments.views.handle_store_authorize')
@patch('shipments.views.handle_app_installed')
@patch('shipments.views.handle_app_uninstalled')
@patch('shipments.views.handle_shipment_creation_or_update')
@patch('shipments.views.parse_shipment_data')
def test_webhook_handler_valid_events(mock_parse_shipment_data, mock_handle_shipment_creation_or_update,
                                      mock_handle_app_uninstalled, mock_handle_app_installed,
                                      mock_handle_store_authorize, rf):
    url = reverse('webhook_handler')
    data_store_authorize = json.dumps({"event": "app.store.authorize", "merchant": 123,
                                       "data": {"access_token": "abc123", "refresh_token": "def456",
                                                "expires": 1609459200}})
    data_app_installed = json.dumps({"event": "app.installed", "merchant": 123})
    data_app_uninstalled = json.dumps({"event": "app.uninstalled", "merchant": 123})
    data_shipment_creating = json.dumps(
        {"event": "shipment.creating", "created_at": "Sat Jan 01 2022 12:00:00 GMT+0000 (UTC)",
         "data": {"id": 1, "status": "created"}})
    data_shipment_cancelled = json.dumps(
        {"event": "shipment.cancelled", "created_at": "Sat Jan 01 2022 12:00:00 GMT+0000 (UTC)",
         "data": {"id": 1, "status": "cancelled"}})

    request_store_authorize = rf.post(url, data_store_authorize, content_type='application/json')
    request_app_installed = rf.post(url, data_app_installed, content_type='application/json')
    request_app_uninstalled = rf.post(url, data_app_uninstalled, content_type='application/json')
    request_shipment_creating = rf.post(url, data_shipment_creating, content_type='application/json')
    request_shipment_cancelled = rf.post(url, data_shipment_cancelled, content_type='application/json')

    mock_parse_shipment_data.return_value = ({"shipment_id": 1}, "created")

    # Test store authorize event
    response = webhook_handler(request_store_authorize)
    assert response.status_code == 201
    mock_handle_store_authorize.assert_called_once()

    # Test app installed event
    response = webhook_handler(request_app_installed)
    assert response.status_code == 200
    mock_handle_app_installed.assert_called_once()

    # Test app uninstalled event
    response = webhook_handler(request_app_uninstalled)
    assert response.status_code == 200
    mock_handle_app_uninstalled.assert_called_once()

    # Test shipment creating event
    response = webhook_handler(request_shipment_creating)
    assert response.status_code == 201
    mock_handle_shipment_creation_or_update.assert_called_once()

    # Test shipment cancelled event
    response = webhook_handler(request_shipment_cancelled)
    assert response.status_code == 201
    mock_handle_shipment_creation_or_update.assert_called()


@pytest.mark.django_db
def test_webhook_handler_invalid_json(rf):
    url = reverse('webhook_handler')
    request = rf.post(url, "invalid_json", content_type='application/json')

    response = webhook_handler(request)

    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid JSON data'}


@pytest.mark.django_db
def test_webhook_handler_unknown_event(rf):
    url = reverse('webhook_handler')
    data = json.dumps({"event": "unknown.event"})
    request = rf.post(url, data, content_type='application/json')

    response = webhook_handler(request)

    assert response.status_code == 400
    assert response.json() == {'error': 'Unknown event type'}


@pytest.mark.django_db
def test_webhook_handler_method_not_allowed(rf):
    url = reverse('webhook_handler')
    request = rf.get(url)

    response = webhook_handler(request)

    assert response.status_code == 405
    assert response.json() == {'error': 'Method not allowed'}
