import pytest
from django.urls import reverse
from django.http import JsonResponse
from unittest.mock import patch, Mock
from shipments.models import Shipment, ShipmentStatus
from shipments.services.shipment_service import handle_shipment_creation_or_update


@pytest.mark.django_db
@patch('shipments.services.shipment_service.handle_shipment_update')
@patch('shipments.services.shipment_service.handle_status_update')
def test_handle_shipment_creation_or_update_new_shipment(mock_handle_status_update, mock_handle_shipment_update, rf):
    shipment_data = {
        'shipment_id': 123,
        'type': 'new',
        'merchant': 456,
        'event': 'test_event',
        'created_at': '2023-01-01T00:00:00Z',
        'courier_name': 'Test Courier',
        'shipping_number': '123456789012',
    }
    request = rf.get('/shipments/create')

    response = handle_shipment_creation_or_update(shipment_data, 'created', request)

    assert response.status_code == 201
    assert Shipment.objects.filter(shipment_id=123).exists()
    assert mock_handle_status_update.called_once_with(123, 'created')
    assert not mock_handle_shipment_update.called


@pytest.mark.django_db
@patch('shipments.services.shipment_service.handle_status_update')
def test_handle_shipment_creation_or_update_existing_shipment(mock_handle_status_update, rf):
    shipment = Shipment.objects.create(
        shipment_id=123,
        type='existing',
        merchant=456,
        event='test_event',
        created_at='2023-01-01T00:00:00Z',
        courier_name='Test Courier',
        shipping_number='123456789012',
    )
    shipment_data = {
        'shipment_id': 123,
        'type': 'existing',
        'merchant': 456,
        'event': 'test_event',
        'created_at': '2023-01-01T00:00:00Z',
        'courier_name': 'Test Courier',
        'shipping_number': '123456789012',
    }
    request = rf.get('/shipments/update')

    response = handle_shipment_creation_or_update(shipment_data, 'created', request)

    assert response.status_code == 200
    assert mock_handle_status_update.called_once_with(123, 'created')


@pytest.mark.django_db
@patch('shipments.services.shipment_service.handle_status_update')
@patch('shipments.services.shipment_service.handle_shipment_update')
def test_handle_shipment_creation_or_update_return_shipment(mock_handle_shipment_update, mock_handle_status_update, rf):
    shipment = Shipment.objects.create(
        shipment_id=123,
        type='return',
        merchant=456,
        event='test_event',
        created_at='2023-01-01T00:00:00Z',
        courier_name='Test Courier',
        shipping_number='123456789012',
    )
    shipment_data = {
        'shipment_id': 123,
        'type': 'return',
        'merchant': 456,
        'event': 'test_event',
        'created_at': '2023-01-01T00:00:00Z',
        'courier_name': 'Test Courier',
        'shipping_number': '123456789012',
    }
    request = rf.get('/shipments/update')

    response = handle_shipment_creation_or_update(shipment_data, 'created', request)

    assert response.status_code == 200
    assert mock_handle_shipment_update.called_once_with(shipment_data)
    assert mock_handle_status_update.called_once_with(123, 'created')


@pytest.mark.django_db
@patch('shipments.services.shipment_service.logger')
def test_handle_shipment_creation_or_update_error(mock_logger, rf):
    shipment_data = {
        'shipment_id': 123,
        'type': 'new',
        'merchant': 456,
        'event': 'test_event',
        'created_at': '2023-01-01T00:00:00Z',
        'courier_name': 'Test Courier',
        'shipping_number': '123456789012',
    }
    request = rf.get('/shipments/create')

    with patch('app.models.Shipment.objects.create') as mock_create:
        mock_create.side_effect = Exception('Test Exception')
        response = handle_shipment_creation_or_update(shipment_data, 'created', request)

    assert response.status_code == 500
    assert 'Error in handle_shipment_creation_or_update' in mock_logger.error.call_args[0][0]
