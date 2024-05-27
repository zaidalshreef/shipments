import logging
from django.http import JsonResponse
from ..models import Shipment, ShipmentStatus
from django.urls import reverse
from .salla_service import update_salla_api
from .email_service import send_shipment_email
from datetime import datetime

# Initialize the logger
logger = logging.getLogger(__name__)


def handle_shipment_creation_or_update(shipment_data, status, request):
    logger.info(
        f"Handling shipment creation or update for shipment_id: {shipment_data.get('shipment_id')}, status: {status}")
    try:
        existing_shipment = Shipment.objects.filter(shipment_id=shipment_data.get('shipment_id')).first()
        send_shipment_email(shipment_data, status)
        if existing_shipment and shipment_data.get('type') == 'return':
            logger.info(f"Updating return shipment: {shipment_data.get('shipment_id')}")
            handle_shipment_update(shipment_data)
            return handle_status_update(shipment_data.get('shipment_id'), status)
        elif existing_shipment and status == 'cancelled':
            logger.info(f"Updating cancelled shipment: {shipment_data.get('shipment_id')}")
            return handle_status_update(shipment_data.get('shipment_id'), status)
        elif existing_shipment:
            logger.info(f"Updating existing shipment: {shipment_data.get('shipment_id')}")
            return handle_status_update(shipment_data.get('shipment_id'), status)
        else:
            logger.info(f"Creating new shipment: {shipment_data.get('shipment_id')}")
            shipment = handle_shipment_creation(shipment_data, request)
            handle_status_update(shipment.shipment_id, status)
            return JsonResponse({'message': 'Shipment created successfully', 'shipment_id': shipment.shipment_id}, status=201)
    except Exception as e:
        logger.error(f"Error in handle_shipment_creation_or_update: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_shipment_creation(shipment_data, request):
    logger.info(f"Creating shipment with data: {shipment_data}")
    try:
        new_shipment = Shipment(**shipment_data)
        new_shipment.save()

        pdf_label_url = request.build_absolute_uri(
            reverse('shipments:generate_pdf_label', args=[new_shipment.shipment_id])
        )
        new_shipment.label = {'url': pdf_label_url}
        new_shipment.save()

        logger.info(f"Shipment created successfully with ID: {new_shipment.shipment_id}")
        return new_shipment
    except Exception as e:
        logger.error(f"Error in handle_shipment_creation: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_shipment_update(shipment_data):
    logger.info(f"Updating shipment with data: {shipment_data}")
    try:
        if shipment_data is None:
            logger.warning("No shipment data provided")
            return JsonResponse({'error': 'No shipment data provided'}, status=400)

        shipment_id = shipment_data.get('shipment_id')
        if shipment_id is None:
            logger.warning("Missing shipping id in payload")
            return JsonResponse({'error': 'Missing shipping id in payload'}, status=400)

        shipment = Shipment.objects.get(shipment_id=shipment_id)
        for key, value in shipment_data.items():
            setattr(shipment, key, value)
        shipment.save()

        logger.info(f"Shipment update event processed for shipment_id: {shipment_id}")
        return JsonResponse({'message': 'Shipment update event processed'}, status=200)
    except Shipment.DoesNotExist:
        logger.error(f"Shipment with shipment_id {shipment_id} does not exist.")
        return JsonResponse({'error': f"Shipment with shipment_id {shipment_id} does not exist."}, status=400)
    except Exception as e:
        logger.error(f"Error in handle_shipment_update: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_status_update(shipment_id, status):
    logger.info(f"Updating status for shipment_id: {shipment_id} to {status}")
    try:
        shipment = Shipment.objects.get(shipment_id=shipment_id)
        new_status = ShipmentStatus(
            shipment=shipment,
            status=status
        )
        new_status.save()
        if status != 'cancelled':
            update_salla_api(shipment, status)
        logger.info(f"Shipment status updated successfully for shipment_id: {shipment_id}")
        return JsonResponse({'message': 'Shipment status updated successfully'}, status=200)
    except Shipment.DoesNotExist:
        logger.error(f"Shipment not found for shipment_id {shipment_id}")
        return JsonResponse({'error': 'Shipment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in handle_status_update: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def parse_shipment_data(data):
    logger.info(f"Parsing shipment data: {data}")
    try:
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

        logger.info(f"Parsed shipment data successfully: {shipment_data}")
        return shipment_data, status
    except Exception as e:
        logger.error(f"Error in parse_shipment_data: {str(e)}")
        raise ValueError(f"Error parsing shipment data: {str(e)}")
