from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShipmentForm, ShipmentStatusForm
from .models import Shipment
from .services import update_salla_api, handle_status_update, handle_shipment_update


def home(request):
    shipments = Shipment.objects.all()

    return render(request, 'home.html', {'shipments': shipments})


def shipment_list(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipment_list.html', {'shipments': shipments})


def shipment_detail(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    return render(request, 'shipment_detail.html', {'shipment': shipment})


def update_shipment_details(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            shipment = form.save()  # Save the form data to the instance
            handle_shipment_update(shipment)  # Pass the shipment instance to the handle_shipment_update function
            return redirect('shipment_detail', id=shipment_id)
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, 'shipment_form.html', {'form': form})


def update_status(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if request.method == 'POST':
        form = ShipmentStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            handle_status_update(shipment_id, status)  # Pass the status to the handle_status_update function
            return redirect('shipment_detail', id=shipment_id)
    else:
        form = ShipmentStatusForm()
    return render(request, 'update_status_form.html', {'form': form, 'shipment': shipment})


def shipment_delete(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if request.method == 'POST':
        shipment.delete()
        return redirect('shipment_list')
    return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
