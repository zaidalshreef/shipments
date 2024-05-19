import json
from django.test import RequestFactory, TestCase
from unittest.mock import patch
from .models import Shipment
from .services import (
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
            'data': {
                'id': 123,
                'status': 'shipped',
                'shipping_number': '1234567890'
            }
        }
        request = self.factory.post('/webhook/', data=json.dumps(payload), content_type='application/json')
        response = webhook_handler(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Shipment creation event processed'})

    def test_webhook_handler_invalid_json_payload(self):
        request = self.factory.post('/webhook/', data="invalid_payload", content_type='application/json')
        response = webhook_handler(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Invalid JSON data'})

    def test_webhook_handler_missing_data(self):
        payload = {'event': 'shipment.creating'}
        request = self.factory.post('/webhook/', data=json.dumps(payload), content_type='application/json')
        response = webhook_handler(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Missing data in shipment_data'})


class HandleShipmentCreationTestCase(TestCase):

    @patch('shipments.services.save_to_database')
    def test_handle_shipment_creation_valid_payload(self, mock_save_to_database):
        payload = {
            'event': 'shipment.creating',
            'merchant': 123,
            'created_at': '2024-05-10T12:00:00Z',
            'data': {
                'id': 123,
                'status': 'shipped',
                'shipping_number': '1234567890'
            }
        }
        response = handle_shipment_creation(payload, payload['data']['status'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Shipment creation event processed'})
        mock_save_to_database.assert_called_once_with(payload, payload['data']['status'])

    def test_handle_shipment_creation_invalid_payload(self):
        payload = {'event': 'shipment.creating'}
        response = handle_shipment_creation(payload, None)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Invalid shipment data provided'})


class HandleShipmentUpdateTestCase(TestCase):

    @patch('shipments.services.update_database')
    def test_handle_shipment_update_valid_payload(self, mock_update_database):
        payload = {
            'event': 'shipment.updated',
            'merchant': 123,
            'created_at': '2024-05-10T12:00:00Z',
            'data': {
                'id': 123,
                'status': 'shipped',
                'shipping_number': '1234567890'
            }
        }
        response = handle_shipment_update(payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Shipment update event processed'})
        mock_update_database.assert_called_once_with(payload)

    def test_handle_shipment_update_invalid_payload(self):
        payload = {'event': 'shipment.updated'}
        response = handle_shipment_update(payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Missing shipping id in payload'})
