from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShipmentForm, ShipmentStatusForm
from .models import Shipment
from .services import update_salla_api, handle_status_update


def home(request):
    shipments = Shipment.objects.all()

    return render(request, 'home.html', {'shipments': shipments})


def shipment_list(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipment_list.html', {'shipments': shipments})


def shipment_detail(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    return render(request, 'shipment_detail.html', {'shipment': shipment})


def update_shipment_details(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            form.save()
            # Get the last status of the shipment
            last_status = shipment.statuses.latest('date_time').status
            update_salla_api(shipment, last_status)  # Pass the last status to the Salla API update function
            return redirect('shipment_detail', id=id)
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, 'shipment_form.html', {'form': form})


def update_status(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    if request.method == 'POST':
        form = ShipmentStatusForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.shipment = shipment
            status.save()
            update_salla_api(shipment, status.status)  # Update Salla API with new status
            return redirect('shipment_detail', id=id)
    else:
        form = ShipmentStatusForm()
    return render(request, 'update_status_form.html', {'form': form, 'shipment': shipment})


def shipment_delete(request, id):
    shipment = get_object_or_404(Shipment, id=id)
    if request.method == 'POST':
        shipment.delete()
        return redirect('shipment_list')
    return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
