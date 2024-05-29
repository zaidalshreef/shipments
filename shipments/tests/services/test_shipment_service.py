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
        'event': 'shipment.creating',
        'merchant': 123,
        'created_at': 'Wed Oct 13 2021 07:53:00 GMT+0000 (UTC)',
        'data': {
            'id': 1,
            'status': 'creating',
            'type': 'shipment',
            'courier_name': 'DHL',
            'payment_method': 'COD',
            'total': {'amount': 100, 'currency': 'USD'},
            'cash_on_delivery': {'amount': 10, 'currency': 'USD'},
            'label': {'url': 'http://example.com/label.pdf', 'format': 'pdf'},
            'total_weight': {'weight': 5, 'unit': 'kg'},
            'packages': [{'id': 1, 'weight': 5}],
            'ship_from': {'address': '123 Street, City, Country'},
            'ship_to': {'address': '456 Avenue, City, Country'},
            'meta': {'info': 'some info'},
        }
    }

    response = handle_shipment_creation_or_update(shipment_data, 'created', request)

    assert response.status_code == 201
    assert Shipment.objects.filter(shipment_id=1).exists()  # Correct shipment_id to 1
    mock_handle_status_update.assert_called_once_with(1, 'created')
    mock_handle_shipment_update.assert_not_called()


@pytest.mark.django_db
def test_handle_shipment_creation_or_update_existing_shipment(mocker):
    mock_shipment = mocker.Mock()
    mocker.patch('shipments.services.shipment_service.Shipment.objects.filter', return_value=[mock_shipment])
    mock_handle_status_update = mocker.patch('shipments.services.shipment_service.handle_status_update',
                                             return_value=mocker.Mock(status_code=200))

    response = handle_shipment_creation_or_update({'shipment_id': 1}, 'created', mocker.Mock())

    assert response.status_code == 200
    mock_handle_status_update.assert_called_once()


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

    with patch('shipments.models.Shipment.objects.create') as mock_create:
        mock_create.side_effect = Exception('Test Exception')
        response = handle_shipment_creation_or_update(shipment_data, 'created', request)

    assert response.status_code == 500
    assert 'Error in handle_shipment_creation_or_update' in mock_logger.error.call_args[0][0]
