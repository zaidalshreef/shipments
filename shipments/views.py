from django.shortcuts import render, redirect, get_object_or_404
from .models import Shipment
from .forms import ShipmentForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def webhook_handler(request):
    if request.method == 'POST':
        # Parse the JSON payload
        try:
            payload = json.loads(request.body)
            event_type = payload.get('event')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        # Validate payload contents
        if 'data' not in payload:
            return JsonResponse({'error': 'Missing data in payload'}, status=400)

        # Process the payload based on the event type
        if event_type == 'shipment.creating':
            return handle_shipment_creation(payload)
        elif event_type == 'shipment.updated':
            return handle_shipment_update(payload)
        else:
            return JsonResponse({'error': 'Unknown event type'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def handle_shipment_creation(payload):
    shipment_data = payload.get('data')
    if not shipment_data:
        return JsonResponse({'error': 'No shipment data provided'}, status=400)
    # Perform actions related to shipment creation
    save_to_database(shipment_data)
    return JsonResponse({'message': 'Shipment creation event processed'})


def handle_shipment_update(payload):
    shipment_data = payload.get('data')
    if not shipment_data:
        return JsonResponse({'error': 'No shipment data provided'}, status=400)
    # Perform actions related to shipment update
    update_database(shipment_data)
    return JsonResponse({'message': 'Shipment update event processed'})


def save_to_database(shipment_data):
    # Extract relevant data from the payload and create a new Shipment object
    new_shipment = Shipment(
        event=shipment_data.get('event'),
        merchant=shipment_data.get('merchant'),
        created_at=shipment_data.get('created_at'),
        status=shipment_data.get('status'),
        shipping_number=shipment_data.get('shipping_number'),
        data=shipment_data  # Save the entire payload as JSON data
    )
    # Save the new shipment to the database
    new_shipment.save()

def update_database(shipment_data):
    # Extract relevant data from the payload to identify the shipment to update
    shipping_number = shipment_data.get('shipping_number')
    # Retrieve the corresponding shipment object from the database
    shipment = Shipment.objects.get(shipping_number=shipping_number)
    # Update the shipment attributes based on the payload
    shipment.event = shipment_data.get('event')
    shipment.merchant = shipment_data.get('merchant')
    shipment.created_at = shipment_data.get('created_at')
    shipment.status = shipment_data.get('status')
    # Update additional fields as needed
    # Save the updated shipment to the database
    shipment.save()

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
