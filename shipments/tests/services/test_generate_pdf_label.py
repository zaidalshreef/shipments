import pytest
from django.urls import reverse
from django.http import HttpRequest
from django.template.loader import render_to_string
from weasyprint import HTML
from shipments.models import Shipment
from shipments.services.pdf_service import generate_pdf_label


@pytest.mark.django_db
def test_generate_pdf_label_success(mocker):
    shipment = Shipment.objects.create(
        shipment_id=1,
        event='test_event',
        merchant=123,
        created_at='2023-01-01T00:00:00Z',
        type='test_type',
        shipping_number='123456',
        courier_name='Test Courier',
        courier_logo='https://example.com/logo.png',
        tracking_number='TN123456',
        tracking_link='https://example.com/tracking',
        payment_method='cash',
        total={},
        cash_on_delivery={},
        label={},
        total_weight={},
        created_at_details={},
        packages={},
        ship_from={},
        ship_to={},
        meta={}
    )

    request = HttpRequest()
    request.method = 'GET'

    mocker.patch('shipments.services.pdf_service.render_to_string', return_value='<html></html>')
    mocker.patch('weasyprint.HTML.write_pdf', return_value=b'PDF content')

    response = generate_pdf_label(request, shipment.shipment_id)
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert response['Content-Disposition'] == 'attachment; filename="shipment_label_1.pdf"'
    assert response.content == b'PDF content'


@pytest.mark.django_db
def test_generate_pdf_label_shipment_not_found(mocker):
    request = HttpRequest()
    request.method = 'GET'

    response = generate_pdf_label(request, 999)
    assert response.status_code == 404
    assert response.json() == {'error': 'Shipment not found'}


@pytest.mark.django_db
def test_generate_pdf_label_internal_server_error(mocker):
    shipment = Shipment.objects.create(
        shipment_id=1,
        event='test_event',
        merchant=123,
        created_at='2023-01-01T00:00:00Z',
        type='test_type',
        shipping_number='123456',
        courier_name='Test Courier',
        courier_logo='https://example.com/logo.png',
        tracking_number='TN123456',
        tracking_link='https://example.com/tracking',
        payment_method='cash',
        total={},
        cash_on_delivery={},
        label={},
        total_weight={},
        created_at_details={},
        packages={},
        ship_from={},
        ship_to={},
        meta={}
    )

    request = HttpRequest()
    request.method = 'GET'

    mocker.patch('shipments.services.pdf_service.render_to_string', side_effect=Exception('Render error'))
    response = generate_pdf_label(request, shipment.shipment_id)
    assert response.status_code == 500
    assert response.json() == {'error': 'Internal server error'}

    mocker.patch('shipments.services.pdf_service.render_to_string', return_value='<html></html>')
    mocker.patch('weasyprint.HTML.write_pdf', side_effect=Exception('PDF error'))

    response = generate_pdf_label(request, shipment.shipment_id)
    assert response.status_code == 500
    assert response.json() == {'error': 'Internal server error'}
