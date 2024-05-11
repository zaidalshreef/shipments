import json
from django.test import RequestFactory, TestCase
from unittest.mock import patch, MagicMock
from .models import Shipment
from .views import (
    handle_shipment_creation,
    handle_shipment_update,
    save_to_database,
    update_database,
    webhook_handler,
)
from django.core.exceptions import ObjectDoesNotExist


class TestWebhookHandler(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_webhook_handler_valid_payload(self):
        payload = {
            'event': 'shipment.creating',
            'merchant': 123,
            'created_at': '2024-05-10T12:00:00Z',
            'status': 'shipped',
            'shipping_number': '1234567890',
            'data': {'shipment_id': 123}
        }
        request = self.factory.post('/webhook/', data=json.dumps(payload), content_type='application/json')
        response = webhook_handler(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Shipment creation event processed'})

    def test_webhook_handler_invalid_json_payload(self):
        request = self.factory.post('/webhook/', data="invalid_payload", content_type='application/json')
        response = webhook_handler(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Invalid JSON payload'})

    def test_webhook_handler_missing_data(self):
        payload = {'event': 'shipment.creating'}
        request = self.factory.post('/webhook/', data=json.dumps(payload), content_type='application/json')
        response = webhook_handler(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Missing data in payload'})


class HandleShipmentCreationTestCase(TestCase):

    @patch('shipments.views.save_to_database')
    def test_handle_shipment_creation_valid_payload(self, mock_save_to_database):
        # Valid payload with shipment data provided
        payload = {
            'event': 'shipment.updated',
            'merchant': 123,
            'created_at': '2024-05-10T12:00:00Z',
            'status': 'shipped',
            'shipping_number': '1234567890',
            'data': {'shipment_id': 123}
        }
        response = handle_shipment_creation(payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Shipment creation event processed'})
        mock_save_to_database.assert_called_once_with(payload)

    def test_handle_shipment_creation_invalid_payload(self):
        # Invalid payload with no shipment data provided
        payload = {'event': 'shipment.creating'}  # Missing 'data' field
        response = handle_shipment_creation(payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Invalid shipment data provided'})

    @patch('shipments.views.save_to_database')
    def test_handle_shipment_creation_calls_save_to_database(self, mock_save_to_database):
        # Ensure that save_to_database is called with the correct payload data
        payload = {
            'event': 'shipment.updated',
            'merchant': 123,
            'created_at': '2024-05-10T12:00:00Z',
            'status': 'shipped',
            'shipping_number': '1234567890',
            'data': {'shipment_id': 123}
        }
        handle_shipment_creation(payload)
        mock_save_to_database.assert_called_once_with(payload)


class HandleShipmentUpdateTestCase(TestCase):

    @patch('shipments.views.update_database')
    def test_handle_shipment_update_valid_payload(self, mock_update_database):
        # Valid payload with shipment data provided
        payload = {
            'event': 'shipment.updated',
            'merchant': 123,
            'created_at': '2024-05-10T12:00:00Z',
            'status': 'shipped',
            'shipping_number': '1234567890',
            'data': {'shipment_id': 123}
        }
        response = handle_shipment_update(payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Shipment update event processed'})
        mock_update_database.assert_called_once_with(payload)

    def test_handle_shipment_update_invalid_payload(self):
        # Invalid payload with no shipment data provided
        payload = {'event': 'shipment.updated'}  # Missing 'data' field
        response = handle_shipment_update(payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Missing shipping number in payload'})

    @patch('shipments.views.update_database')
    def test_handle_shipment_update_calls_update_database(self, mock_update_database):
        # Ensure that update_database is called with the correct payload data
        payload = {
            'event': 'shipment.updated',
            'merchant': 123,
            'created_at': '2024-05-10T12:00:00Z',
            'status': 'shipped',
            'shipping_number': '1234567890',
            'data': {'shipment_id': 123}
        }
        handle_shipment_update(payload)
        mock_update_database.assert_called_once_with(payload)


