import logging
import json
from django.http import JsonResponse
from ..models import Shipment, ShipmentStatus
from django.urls import reverse
from .salla_service import update_salla_api
from .notification_service import send_shipment_email, send_sms, send_whatsapp
from datetime import datetime

# Initialize the logger
logger = logging.getLogger(__name__)


def handle_shipment_creation_or_update(shipment_data, status, request):
    """
    Handles shipment creation or update based on the provided shipment data, status, and request.

    Args:
    shipment_data (dict): A dictionary containing the shipment data.
    status (str): The status of the shipment.
    request (HttpRequest): The HTTP request object.

    Returns:
    JsonResponse: A JSON response containing a message and the shipment ID if the shipment is created successfully.
    JsonResponse: A JSON response containing an error message if an error occurs during shipment creation or update.

    Raises:
    Exception: If an error occurs during shipment creation or update.

    This function first checks if an existing shipment with the same shipment ID exists. If it does, it handles the update accordingly. If the shipment is a return shipment, it updates the return shipment. If the status is 'cancelled', it updates the cancelled shipment. If the shipment is an existing shipment, it updates the existing shipment. If the shipment is a new shipment, it creates a new shipment, updates the status, and returns a JSON response with a success message and the shipment ID. If an error occurs during shipment creation or update, it logs the error and returns a JSON response with an error message.
    """
    try:
        existing_shipment = Shipment.objects.filter(shipment_id=shipment_data.get('shipment_id')).first()
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
            return JsonResponse({'message': 'Shipment created successfully', 'shipment_id': shipment.shipment_id},
                                status=201)
    except Exception as e:
        logger.error(f"Error in handle_shipment_creation_or_update: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_shipment_creation(shipment_data, request):
    """
    Creates a new shipment and returns the newly created shipment object.

    Args:
    shipment_data (dict): A dictionary containing the shipment data.
    request (HttpRequest): The HTTP request object.

    Returns:
    Shipment: A Shipment object representing the newly created shipment.

    Raises:
    Exception: If an error occurs during shipment creation.

    This function first creates a new Shipment object using the provided shipment data. It then saves the new shipment to the database. After that, it generates a PDF label for the shipment and saves it to the Shipment object. Finally, it returns the newly created shipment object. If an error occurs during shipment creation, it logs the error and returns a JSON response with an error message.
    """
    shipment_id = shipment_data.get('shipment_id')
    logger.info(f"Creating shipment with ID:{shipment_id}")
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
    """
    Updates an existing shipment based on the provided shipment data.

    Args:
    shipment_data (dict): A dictionary containing the shipment data.

    Returns:
    JsonResponse: A JSON response containing a message and the shipment ID if the shipment is updated successfully.

    Raises:
    Exception: If an error occurs during shipment update.

    This function first checks if the provided shipment data contains a shipment ID. If it does, it retrieves the corresponding Shipment object from the database. It then iterates through the key-value pairs in the shipment data and updates the corresponding attributes of the Shipment object. Finally, it saves the updated Shipment object to the database and returns a JSON response with a success message and the shipment ID. If an error occurs during shipment update, it logs the error and returns a JSON response with an error message.
    """
    shipment_id = shipment_data.get('shipment_id')

    if shipment_id is None:
        logger.warning("Missing shipping id in payload")
        return JsonResponse({'error': 'Missing shipping id in payload'}, status=400)

    logger.info(f"Updating shipment with ID: {shipment_id}")

    try:
        if shipment_data is None:
            logger.warning("No shipment data provided")
            return JsonResponse({'error': 'No shipment data provided'}, status=400)

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
    """
    Updates the status of a shipment in the database and performs additional actions based on the status.

    Args:
    shipment_id (str): The unique identifier of the shipment.
    status (str): The new status of the shipment.

    Returns:
    JsonResponse: A JSON response containing a message and the shipment ID if the status update is successful.

    Raises:
    Shipment.DoesNotExist: If the shipment with the given shipment ID does not exist.
    Exception: If an error occurs during the status update process.

    This function first retrieves the Shipment object with the given shipment ID from the database. It then creates a new ShipmentStatus object with the provided status and the retrieved Shipment object. The new ShipmentStatus object is saved to the database. Depending on the new status, additional actions are performed. If the status is 'created' or 'cancelled', a shipment email is sent. If the status is 'delivery', a shipment SMS is sent. If the status is not 'cancelled', the SALLA API is updated. Finally, a JSON response containing a success message and the shipment ID is returned if the status update is successful. If the shipment with the given shipment ID does not exist, a 'Shipment not found' error message is returned. If an error occurs during the status update process, an error message containing the error details is returned.
    """
    logger.info(f"Updating status for shipment_id: {shipment_id} to {status}")
    try:
        shipment = Shipment.objects.get(shipment_id=shipment_id)
        new_status = ShipmentStatus(
            shipment=shipment,
            status=status
        )
        new_status.save()
        if status == 'created' or status == 'cancelled':
            send_shipment_email(shipment, status)
        # if status == 'delivery':
        #    send_sms(shipment)
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
    """
    Parses the provided shipment data and returns a dictionary containing the parsed data.

    Args:
    data (dict): A dictionary containing the shipment data.

    Returns:
    tuple: A tuple containing a dictionary of parsed shipment data and the status of the shipment.

    Raises:
    ValueError: If the 'created_at' field is missing in the shipment data.

    This function first checks if the 'created_at' field is present in the shipment data. If it is, it parses the 'created_at' field using the 'datetime' module and formats it as an ISO 8601 string. It then extracts the remaining shipment data from the 'data' field of the input dictionary. The parsed shipment data is then formatted as a JSON string and logged using the 'logger' object. Finally, the parsed shipment data and the status of the shipment are returned as a tuple. If the 'created_at' field is missing in the shipment data, a ValueError is raised with an appropriate error message.
    """
    formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
    logger.info(f"Parsing shipment data:\n{formatted_data}")
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
        formatted_data = json.dumps(shipment_data, indent=4, ensure_ascii=False)
        logger.info(f"Parsed shipment data successfully:\n{formatted_data}")
        return shipment_data, status
    except Exception as e:
        logger.error(f"Error in parse_shipment_data: {str(e)}")
        raise ValueError(f"Error parsing shipment data: {str(e)}")
