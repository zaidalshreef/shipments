import pytest
import logging
import requests
import json
import pytz
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import make_aware
from django.http import JsonResponse
from shipments.models import MerchantToken
from shipments.services.salla_service import handle_store_authorize, handle_app_installed, handle_app_uninstalled, \
    refresh_token, get_access_token, update_salla_api


@pytest.mark.django_db
def test_handle_store_authorize():
    data = {
        'merchant': 123,
        'data': {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires': int((timezone.now() + timedelta(hours=1)).timestamp())
        }
    }
    response = handle_store_authorize(data)
    assert response.status_code == 201
    assert MerchantToken.objects.filter(merchant_id=123).exists()
    merchant_token = MerchantToken.objects.get(merchant_id=123)
    assert merchant_token.access_token == 'test_access_token'
    assert merchant_token.refresh_token == 'test_refresh_token'


@pytest.mark.django_db
def test_handle_store_authorize_failure(mocker):
    mocker.patch('shipments.services.salla_service.MerchantToken.objects.update_or_create',
                 side_effect=Exception('DB error'))
    data = {
        'merchant': 123,
        'data': {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires': int((timezone.now() + timedelta(hours=1)).timestamp())
        }
    }
    response = handle_store_authorize(data)
    assert response.status_code == 500
    assert 'error' in json.loads(response.content)


@pytest.mark.django_db
def test_handle_app_installed():
    data = {
        'merchant': 123
    }
    response = handle_app_installed(data)
    assert response.status_code == 200
    assert 'message' in json.loads(response.content)


@pytest.mark.django_db
def test_handle_app_uninstalled():
    MerchantToken.objects.create(
        merchant_id=123,
        access_token='test_access_token',
        refresh_token='test_refresh_token',
        expires_at=timezone.now() + timedelta(hours=1)
    )
    data = {
        'merchant': 123
    }
    response = handle_app_uninstalled(data)
    assert response.status_code == 200
    assert MerchantToken.objects.filter(merchant_id=123).exists()


@pytest.mark.django_db
def test_refresh_token_success(mocker):
    merchant_token = MerchantToken.objects.create(
        merchant_id=123,
        access_token='old_access_token',
        refresh_token='test_refresh_token',
        expires_at=timezone.now() - timedelta(hours=1)
    )
    mocker.patch('requests.post', return_value=mocker.Mock(status_code=200,
                                                           json=lambda: {'access_token': 'new_access_token',
                                                                         'expires': (timezone.now() + timedelta(
                                                                             hours=1)).timestamp()
                                                                         }))
    assert refresh_token(merchant_token) is True
    merchant_token.refresh_from_db()
    assert merchant_token.access_token == 'new_access_token'


@pytest.mark.django_db
def test_refresh_token_failure(mocker):
    merchant_token = MerchantToken.objects.create(
        merchant_id=123,
        access_token='old_access_token',
        refresh_token='test_refresh_token',
        expires_at=timezone.now() - timedelta(hours=1)
    )
    mocker.patch('requests.post', return_value=mocker.Mock(status_code=400, content='Bad Request'))
    assert refresh_token(merchant_token) is False
    merchant_token.refresh_from_db()
    assert merchant_token.access_token == 'old_access_token'


@pytest.mark.django_db
def test_get_access_token_success():
    MerchantToken.objects.create(
        merchant_id=123,
        access_token='test_access_token',
        refresh_token='test_refresh_token',
        expires_at=timezone.now() + timedelta(hours=1)
    )
    token = get_access_token(123)
    assert token == 'test_access_token'


@pytest.mark.django_db
def test_get_access_token_expired(mocker):
    MerchantToken.objects.create(
        merchant_id=123,
        access_token='old_access_token',
        refresh_token='test_refresh_token',
        expires_at=timezone.now() - timedelta(hours=1)
    )
    mocker.patch('requests.post', return_value=mocker.Mock(status_code=200,
                                                           json=lambda: {'access_token': 'new_access_token',
                                                                         'expires': (timezone.now() + timedelta(
                                                                             hours=1)).timestamp()
                                                                         }))
    token = get_access_token(123)
    assert token == 'new_access_token'


@pytest.mark.django_db
def test_get_access_token_failure(mocker):
    mocker.patch('shipments.services.salla_service.MerchantToken.objects.get', side_effect=MerchantToken.DoesNotExist)
    token = get_access_token(123)
    assert token is None


@pytest.mark.django_db
def test_update_salla_api_success(mocker):
    shipment = mocker.Mock()
    shipment.shipment_id = 1
    shipment.shipping_number = '123456'
    shipment.merchant = 123
    shipment.label = {'url': 'https://example.com/label.pdf'}
    mocker.patch('shipments.services.salla_service.get_access_token', return_value='test_access_token')
    mocker.patch('requests.put', return_value=mocker.Mock(status_code=200))

    update_salla_api(shipment, 'created')
    requests.put.assert_called_once()


@pytest.mark.django_db
def test_update_salla_api_failure(mocker):
    shipment = mocker.Mock()
    shipment.shipment_id = 1
    shipment.shipping_number = '123456'
    shipment.merchant = 123
    shipment.label = {'url': 'https://example.com/label.pdf'}
    mocker.patch('shipments.services.salla_service.get_access_token', return_value='test_access_token')
    mocker.patch('requests.put', return_value=mocker.Mock(status_code=400, content='Bad Request'))

    update_salla_api(shipment, 'created')
    requests.put.assert_called_once()


@pytest.mark.django_db
def test_update_salla_api_no_token(mocker):
    logger_error_mock = mocker.patch('shipments.services.salla_service.logger.error')
    shipment = mocker.Mock()
    shipment.merchant = 1
    mocker.patch('shipments.services.salla_service.get_access_token', return_value=None)
    mock_update_salla_api = mocker.patch('shipments.services.salla_service.update_salla_api')

    update_salla_api(shipment, 'created')
    mock_update_salla_api.assert_not_called()
    logger_error_mock.assert_called_once()
    logger_error_mock.assert_called_with('Unable to retrieve access token')
