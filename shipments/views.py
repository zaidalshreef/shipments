from django.shortcuts import render, redirect, get_object_or_404
from .models import Shipment
from .forms import ShipmentForm
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from pprint import pprint

import json


@csrf_exempt
def webhook_handler(request):
    if request.method == 'POST':
        # Parse the JSON payload
        try:
            data = json.loads(request.body)
            created_at_str = data.get('created_at')
            created_at = datetime.strptime(created_at_str, '%a %b %d %Y %H:%M:%S GMT%z')
            created_at_str = created_at.isoformat()
            # Extract relevant data from the payload
            payload = {
                'event': data.get('event'),
                'merchant': data.get('merchant'),
                'created_at': created_at_str,
                'status': data['data'].get('status'),  # Access nested 'status' field
                'shipping_number': data['data'].get('shipping_number'),  # Access nested 'shipping_number' field
                'data': data.get('data')  # Include the entire 'data' object
            }
            event_type = data.get('event')
            pprint(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        # Validate payload contents
        if 'event' not in payload or 'data' not in payload:
            return JsonResponse({'error': 'Missing data in payload'}, status=400)

        # Process the payload based on the event type
        if event_type == 'shipment.creating':
            # Check if a shipment with the same shipping number already exists
            existing_shipment = Shipment.objects.filter(shipping_number=payload.get('shipping_number')).first()
            if existing_shipment:
                return handle_shipment_update(payload)
            else:
                # If the shipment does not exist, create a new shipment object
                return handle_shipment_creation(payload)

        elif event_type == 'shipment.updated':
            return handle_shipment_update(payload)
        else:
            return JsonResponse({'error': 'Unknown event type'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def handle_shipment_creation(payload):
    shipment_data = payload
    required_fields = ['event', 'merchant', 'created_at', 'status', 'shipping_number']
    if not shipment_data:
        return JsonResponse({'error': 'No shipment data provided'}, status=400)
    if not all(field in payload for field in required_fields):
        return JsonResponse({'error': 'Invalid shipment data provided'}, status=400)
    # Perform actions related to shipment creation
    save_to_database(shipment_data)
    return JsonResponse({'message': 'Shipment creation event processed'})


def handle_shipment_update(payload):
    shipment_data = payload
    if shipment_data is None:
        return JsonResponse({'error': 'No shipment data provided'}, status=400)

    shipping_number = shipment_data.get('shipping_number')
    if shipping_number is None:
        return JsonResponse({'error': 'Missing shipping number in payload'}, status=400)

    update_database(shipment_data)
    return JsonResponse({'message': 'Shipment update event processed'})


def save_to_database(shipment_data):
    new_shipment = Shipment(**shipment_data)
    new_shipment.save()


def update_database(shipment_data):
    # Extract relevant data from the payload to identify the shipment to update
    shipping_number = shipment_data.get('shipping_number')

    # Check if the shipment exists in the database
    try:
        shipment = Shipment.objects.get(shipping_number=shipping_number)
    except ObjectDoesNotExist:
        raise ValueError("Shipment with shipping number {} does not exist.".format(shipping_number))

    # Update the shipment attributes based on the payload
    shipment.event = shipment_data.get('event')
    shipment.merchant = shipment_data.get('merchant')
    shipment.created_at = shipment_data.get('created_at')
    shipment.status = shipment_data.get('status')
    # Update additional fields as needed

    # Save the updated shipment to the database
    shipment.save()

def Home(request):
    shipments = Shipment.objects.all()
    
    return render(request, 'Home.html', {'shipments': shipments})

def shipment_list(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipment_list.html', {'shipments': shipments})


def shipment_detail(request, shipping_number):
    shipment = get_object_or_404(Shipment, shipping_number=shipping_number)
    return render(request, 'shipment_detail.html', {'shipment': shipment})


def shipment_create(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shipment_list')
    else:
        form = ShipmentForm()
    return render(request, 'shipment_form.html', {'form': form})


def shipment_update(request, shipping_number):
    shipment = get_object_or_404(Shipment, shipping_number=shipping_number)
    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            form.save()
            return redirect('shipment_detail', shipping_number=shipping_number)
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, 'shipment_form.html', {'form': form})


def shipment_delete(request, shipping_number):
    shipment = get_object_or_404(Shipment, shipping_number=shipping_number)
    if request.method == 'POST':
        shipment.delete()
        return redirect('shipment_list')
    return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
