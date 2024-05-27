from django.http import JsonResponse
from ..models import Shipment, ShipmentStatus
from django.urls import reverse
from .salla_service import update_salla_api
from .email_service import send_shipment_email
from datetime import datetime
import requests
from asgiref.sync import sync_to_async


async def handle_shipment_creation_or_update(shipment_data, status, request):
    send_shipment_email(shipment_data, status)
    existing_shipment = await sync_to_async(
        Shipment.objects.filter(shipment_id=shipment_data.get('shipment_id')).first)()
    if existing_shipment and shipment_data.get('type') == 'return':
        await handle_shipment_update(shipment_data)
        return await handle_status_update(shipment_data.get('shipment_id'), 'created')
    elif existing_shipment and status == 'cancelled':
        return await handle_status_update(shipment_data.get('shipment_id'), status)
    else:
        shipment = await handle_shipment_creation(shipment_data, status)
        pdf_label_url = await request.build_absolute_uri(
            reverse('shipments:generate_pdf_label', args=[shipment.shipment_id]))
        shipment.label = {'url': pdf_label_url}
        await sync_to_async(shipment.save)()
        return JsonResponse({'message': 'Shipment creation event processed', 'pdf_label': pdf_label_url})


async def handle_shipment_creation(shipment_data, status):
    required_fields = ['event', 'merchant', 'created_at', 'shipment_id']
    if not all(field in shipment_data for field in required_fields):
        return JsonResponse({'error': 'Invalid shipment data provided'}, status=400)

    shipment = await save_to_database(shipment_data, status)
    return shipment


async def handle_shipment_update(shipment_data):
    if shipment_data is None:
        return JsonResponse({'error': 'No shipment data provided'}, status=400)

    shipment_id = shipment_data.get('shipment_id')
    if shipment_id is None:
        return JsonResponse({'error': 'Missing shipping id in payload'}, status=400)

    await update_database(shipment_data)
    return JsonResponse({'message': 'Shipment update event processed'}, status=200)


async def save_to_database(shipment_data, status):
    new_shipment = Shipment(**shipment_data)
    await sync_to_async(new_shipment.save)()
    await handle_status_update(new_shipment.shipment_id, status)
    return new_shipment


async def update_database(shipment_data):
    shipment_id = shipment_data.get('shipment_id')
    try:
        shipment = await sync_to_async(Shipment.objects.get)(shipment_id=shipment_id)
    except Shipment.DoesNotExist:
        return JsonResponse({'error': f"Shipment with shipment_id {shipment_id} does not exist."}, status=400)

    for key, value in shipment_data.items():
        setattr(shipment, key, value)
    await sync_to_async(shipment.save)()
    return shipment


async def handle_status_update(shipment_id, status):
    try:
        shipment = await sync_to_async(Shipment.objects.get)(shipment_id=shipment_id)
    except Shipment.DoesNotExist:
        return JsonResponse({'error': 'Shipment not found'}, status=404)

    new_status = ShipmentStatus(
        shipment=shipment,
        status=status
    )
    await sync_to_async(new_status.save)()
    if status != 'cancelled':
        await update_salla_api(shipment, status)
    return JsonResponse({'message': 'Shipment status updated successfully'}, status=200)


def parse_shipment_data(data):
    created_at_str = data.get('created_at')
    if not created_at_str:
        raise ValueError("Missing 'created_at' field in the shipment data")

    created_at = datetime.strptime(created_at_str, '%a %b %d %Y %H:%M:%S GMT%z')
    created_at_str = created_at.isoformat()

    status = data['data'].get('status')

    shipment_data = {
        'event': data.get('event'),
        'merchant': data.get('merchant'),
        'created_at': created_at_str,
        'shipment_id': data['data'].get('id'),
        'type': data['data'].get('type'),
        'courier_name': data['data'].get('courier_name'),
        'courier_logo': data['data'].get('courier_logo'),
        'tracking_number': data['data'].get('tracking_number'),
        'tracking_link': data['data'].get('tracking_link'),
        'payment_method': data['data'].get('payment_method'),
        'total': data['data'].get('total'),
        'cash_on_delivery': data['data'].get('cash_on_delivery'),
        'label': data['data'].get('label'),
        'total_weight': data['data'].get('total_weight'),
        'created_at_details': data['data'].get('created_at'),
        'packages': data['data'].get('packages'),
        'ship_from': data['data'].get('ship_from'),
        'ship_to': data['data'].get('ship_to'),
        'meta': data['data'].get('meta'),
    }

    return shipment_data, status
