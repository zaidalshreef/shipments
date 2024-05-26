import json
from pprint import pprint
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .email_service import send_shipment_email
from .shipment_service import handle_shipment_creation_or_update, handle_status_update, parse_shipment_data
from .salla_service import handle_store_authorize, handle_app_installed


@csrf_exempt
def webhook_handler(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pprint(data)

            if data.get('event') == 'app.store.authorize':
                return handle_store_authorize(data)

            if data.get('event') == 'app.installed':
                return handle_app_installed(data)

            shipment_data, status = parse_shipment_data(data)
            if status == 'creating':
                status = 'created'
            event_type = data.get('event')

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if not shipment_data:
            return JsonResponse({'error': 'Missing data in shipment_data'}, status=400)

        if event_type == 'shipment.creating':
            response = handle_shipment_creation_or_update(shipment_data, status, request)
            send_shipment_email(shipment_data, 'created')
            return response
        elif event_type == 'shipment.cancelled':
            response = handle_status_update(shipment_data.get('shipment_id'), status)
            send_shipment_email(shipment_data, 'cancelled')
            return response
        else:
            return JsonResponse({'error': 'Unknown event type'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
