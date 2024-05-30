import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .salla_service import handle_store_authorize, handle_app_installed, handle_app_uninstalled
from .shipment_service import handle_shipment_creation_or_update, parse_shipment_data

# Initialize the logger
logger = logging.getLogger(__name__)


@csrf_exempt
def webhook_handler(request):
    """
       Handles incoming webhook events from the external system.

       Args:
       request (HttpRequest): The incoming HTTP request.

       Returns:
       HttpResponse: A JSON response containing an error message if the request is invalid, or the result of processing the event.

       Raises:
       ValueError: If the request method is not POST.
       json.JSONDecodeError: If the request body is not valid JSON.

       The function first checks if the request method is POST. If not, it returns a JSON response with an error message.

       If the request method is POST, it attempts to parse the request body as JSON. If this fails, it returns a JSON response with an error message.

       If the parsed JSON contains an 'event' field, the function processes the event accordingly. If the 'event' field is 'app.store.authorize', it calls `handle_store_authorize` with the parsed JSON as argument.

       If the 'event' field is 'app.installed', it calls `handle_app_installed` with the parsed JSON as argument.

       If the 'event' field is 'app.uninstalled', it calls `handle_app_uninstalled` with the parsed JSON as argument.

       If the 'event' field is neither 'app.store.authorize', 'app.installed', nor 'app.uninstalled', the function attempts to parse the shipment data from the parsed JSON. If this fails, it returns a JSON response with an error message.

       If the parsed JSON contains a 'shipment.creating' event, it calls `handle_shipment_creation_or_update` with the parsed shipment data, 'created' status, and the request object as arguments.

       If the parsed JSON contains a 'shipment.cancelled' event, it calls `handle_shipment_creation_or_update` with the parsed shipment data, 'cancelled' status, and the request object as arguments.

       If the parsed JSON contains an unknown event type, it logs a warning message and returns a JSON response with an error message.
       """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event = data.get('event')
            logger.info(f"Received webhook event: {event}")
            if event == 'app.store.authorize':
                logger.info("Calling handle_store_authorize")
                return handle_store_authorize(data)
            elif event == 'app.installed':
                logger.info("Calling handle_app_installed")
                return handle_app_installed(data)
            elif event == 'app.uninstalled':
                logger.info("Calling handle_app_uninstalled")
                return handle_app_uninstalled(data)
            else:
                shipment_data, status = parse_shipment_data(data)
                if event == 'shipment.creating':
                    logger.info("Calling handle_shipment_creation_or_update for creating")
                    return handle_shipment_creation_or_update(shipment_data, "created", request)
                elif event == 'shipment.cancelled':
                    logger.info("Calling handle_shipment_creation_or_update for cancelled")
                    return handle_shipment_creation_or_update(shipment_data, "cancelled", request)
                else:
                    logger.warning(f"Unknown event type: {event}")
                    return JsonResponse({'error': 'Unknown event type'}, status=400)
        except json.JSONDecodeError:
            logger.error("Invalid JSON data received")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        logger.warning(f"Method not allowed: {request.method}")
        return JsonResponse({'error': 'Method not allowed'}, status=405)
