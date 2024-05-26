import json
from pprint import pprint
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .salla_service import handle_store_authorize, handle_app_installed, handle_app_uninstalled
from .shipment_service import handle_shipment_creation_or_update, handle_status_update, parse_shipment_data


@csrf_exempt
def webhook_handler(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event = data.get('event')
            if event == 'app.store.authorize':
                return handle_store_authorize(data)
            elif event == 'app.installed':
                return handle_app_installed(data)
            elif event == 'app.uninstalled':
                return handle_app_uninstalled(data)
            else:
                shipment_data, status = parse_shipment_data(data)
                if event == 'shipment.creating':
                    return handle_shipment_creation_or_update(shipment_data, "created", request)
                elif event == 'shipment.cancelled':
                    return handle_status_update(shipment_data.get('shipment_id'), status)
                else:
                    return JsonResponse({'error': 'Unknown event type'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
