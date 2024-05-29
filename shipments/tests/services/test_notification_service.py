import pytest
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from shipments.models import Shipment
from shipments.services.notification_service import send_shipment_email
from unittest.mock import patch, Mock


@pytest.mark.django_db
@patch('shipments.services.notification_service.send_mail')
@patch('shipments.services.notification_service.render_to_string')
@patch('shipments.services.notification_service.strip_tags')
def test_send_shipment_email_success(mock_strip_tags, mock_render_to_string, mock_send_mail):
    shipment = Shipment.objects.create(
        shipment_id=1,
        event='test_event',
        merchant=123,
        created_at='2023-01-01T00:00:00Z',
        type='test_type',
        shipping_number='123456',
        courier_name='Test Courier',
        courier_logo='http://example.com/logo.png',
        tracking_number='TN123456',
        tracking_link='http://example.com/tracking',
        payment_method='cash',
        total={},
        cash_on_delivery={},
        label={},
        total_weight={},
        created_at_details={},
        packages={},
        ship_from={'name': 'Test From'},
        ship_to={'name': 'Test To'},
        meta={}
    )

    mock_render_to_string.return_value = '<html>Email Content</html>'
    mock_strip_tags.return_value = 'Email Content'

    send_shipment_email(shipment, 'shipped')

    mock_render_to_string.assert_called_once()
    mock_strip_tags.assert_called_once()
    mock_send_mail.assert_called_once_with(
        'Shipment Shipped - 123456',
        'Email Content',
        settings.DEFAULT_FROM_EMAIL,
        settings.INTERNAL_STAFF_EMAILS,
        html_message='<html>Email Content</html>'
    )


@pytest.mark.django_db
@patch('shipments.services.notification_service.send_mail')
@patch('shipments.services.notification_service.render_to_string')
@patch('shipments.services.notification_service.strip_tags')
def test_send_shipment_email_failure(mock_strip_tags, mock_render_to_string, mock_send_mail, caplog):
    shipment = Shipment.objects.create(
        shipment_id=1,
        event='test_event',
        merchant=123,
        created_at='2023-01-01T00:00:00Z',
        type='test_type',
        shipping_number='123456',
        courier_name='Test Courier',
        courier_logo='http://example.com/logo.png',
        tracking_number='TN123456',
        tracking_link='http://example.com/tracking',
        payment_method='cash',
        total={},
        cash_on_delivery={},
        label={},
        total_weight={},
        created_at_details={},
        packages={},
        ship_from={'name': 'Test From'},
        ship_to={'name': 'Test To'},
        meta={}
    )

    mock_render_to_string.side_effect = Exception('Render error')

    with caplog.at_level(logging.ERROR):
        send_shipment_email(shipment, 'shipped')

    assert 'Failed to send email' in caplog.text
    assert mock_render_to_string.called
    assert not mock_strip_tags.called
    assert not mock_send_mail.called
