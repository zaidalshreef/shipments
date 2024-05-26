import json
from pprint import pprint
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..services import handle_store_authorize, handle_app_installed, handle_app_uninstalled, handle_shipment_event


@csrf_exempt
def webhook_handler(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        pprint(data)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    event_type = data.get('event')
    if not event_type:
        return JsonResponse({'error': 'Event type not provided'}, status=400)

    event_handlers = {
        'app.store.authorize': handle_store_authorize,
        'app.installed': handle_app_installed,
        'app.uninstalled': handle_app_uninstalled,
        'shipment.creating': handle_shipment_event,
        'shipment.cancelled': handle_shipment_event
    }

    handler = event_handlers.get(event_type)
    if not handler:
        return JsonResponse({'error': 'Unknown event type'}, status=400)

    return handler(request, data)
