import pytest
import json
from django.urls import reverse
from django.http import JsonResponse
from unittest.mock import patch, Mock, MagicMock
from shipments.models import Shipment, ShipmentStatus
from shipments.services.shipment_service import handle_shipment_creation_or_update
from shipments.services.webhook_service import webhook_handler


@pytest.mark.django_db
@patch('shipments.services.shipment_service.handle_shipment_update')
@patch('shipments.services.shipment_service.handle_status_update')
def test_handle_shipment_creation_or_update_new_shipment(mock_handle_status_update, mock_handle_shipment_update, rf):
    shipment_data = {
        'event': 'shipment.creating',
        'merchant': 123,
        'created_at': 'Wed, 13 Oct 2021 07:53:00 GMT',
        'data': {
            'id': 1,
            'status': 'creating',
            'type': 'shipment',
            'courier_name': 'DHL',
            'payment_method': 'COD',
            'total': {'amount': 100, 'currency': 'USD'},
            'cash_on_delivery': {'amount': 10, 'currency': 'USD'},
            'label': {'url': 'https://example.com/label.pdf', 'format': 'pdf'},
            'total_weight': {'weight': 5, 'unit': 'kg'},
            'packages': [{'id': 1, 'weight': 5}],
            'ship_from': {'address': '123 Street, City, Country'},
            'ship_to': {'address': '456 Avenue, City, Country'},
            'meta': {'info': 'some info'},
        }
    }
    request = rf.post(reverse('shipments:shipment_webhook'), content_type='application/json', data=shipment_data)
    response = webhook_handler(request)
    assert response.status_code == 201
    assert Shipment.objects.filter(shipment_id=1).exists()
    mock_handle_status_update.assert_called_once()
    mock_handle_shipment_update.assert_not_called()


@pytest.mark.django_db
@patch('shipments.services.shipment_service.handle_status_update')
@patch('shipments.services.shipment_service.handle_shipment_update')
def test_handle_shipment_creation_or_update_existing_shipment(mock_handle_status_update, mock_handle_shipment_update, rf):
    existing_shipment = Shipment.objects.create(
        event='shipment.creating',
        merchant=123,
        created_at='2023-01-01T00:00:00Z',
        shipment_id=1,
        type='shipment',
        courier_name='DHL',
        payment_method='COD',
        total={'amount': 100, 'currency': 'USD'},
        cash_on_delivery={'amount': 10, 'currency': 'USD'},
        label={'url': 'https://example.com/label.pdf', 'format': 'pdf'},
        total_weight={'weight': 5, 'unit': 'kg'},
        packages=[{'id': 1, 'weight': 5}],
        ship_from={'address': '123 Street, City, Country'},
        ship_to={'address': '456 Avenue, City, Country'},
        meta={'info': 'some info'}
    )

    shipment_data = {
        'event': 'shipment.cancelled',
        'merchant': 123,
        'created_at': '2023-01-01T00:00:00Z',  # Corrected format
        'data': {
            'id': 1,
            'type': 'shipment',
            'courier_name': 'DHL',
            'payment_method': 'COD',
            'total': {'amount': 100, 'currency': 'USD'},
            'cash_on_delivery': {'amount': 10, 'currency': 'USD'},
            'label': {'url': 'https://example.com/label.pdf', 'format': 'pdf'},
            'total_weight': {'weight': 5, 'unit': 'kg'},
            'packages': [{'id': 1, 'weight': 5}],
            'ship_from': {'address': '123 Street, City, Country'},
            'ship_to': {'address': '456 Avenue, City, Country'},
            'meta': {'info': 'some info'},
        }
    }

    mock_handle_status_update.return_value = MagicMock(status_code=200)
    url = reverse('shipments:shipment_webhook')  # Ensure this matches your URL configuration
    request = rf.post(url, content_type='application/json', data=json.dumps(shipment_data))
    response = webhook_handler(request)
    assert response.status_code == 200
    mock_handle_status_update.assert_called_once()


@pytest.mark.django_db
@patch('shipments.services.shipment_service.handle_status_update')
@patch('shipments.services.shipment_service.handle_shipment_update')
def test_handle_shipment_creation_or_update_return_shipment(mock_handle_shipment_update, mock_handle_status_update, rf):
    shipment = Shipment.objects.create(
        shipment_id=123,
        type='shipment',
        merchant=456,
        event='test_event',
        created_at='2023-01-01T00:00:00Z',
        courier_name='Test Courier',
        shipping_number='123456789012',
    )
    shipment_data = {
        'event': 'shipment.creating',
        'merchant': 456,
        'created_at': 'Wed, 13 Oct 2021 07:53:00 GMT',
        'data': {
            'id': 123,
            'status': 'return',
            'type': 'return',
            'courier_name': 'Test Courier',
            'payment_method': 'COD',
            'total': {'amount': 100, 'currency': 'USD'},
            'cash_on_delivery': {'amount': 10, 'currency': 'USD'},
            'label': {'url': 'https://example.com/label.pdf', 'format': 'pdf'},
            'total_weight': {'weight': 5, 'unit': 'kg'},
            'packages': [{'id': 1, 'weight': 5}],
            'ship_from': {'address': '123 Street, City, Country'},
            'ship_to': {'address': '456 Avenue, City, Country'},
            'meta': {'info': 'some info'},
        }
    }
    mock_handle_status_update.return_value = MagicMock(status_code=200)
    request = rf.post(reverse('shipments:shipment_webhook'), content_type='application/json', data=shipment_data)
    response = webhook_handler(request)
    assert response.status_code == 200
    assert mock_handle_shipment_update.called_once_with(shipment_data)
    assert mock_handle_status_update.called_once_with(123, 'created')


