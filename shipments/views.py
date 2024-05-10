from django.shortcuts import render, redirect, get_object_or_404
from .models import Shipment
from .forms import ShipmentForm


def shipment_list(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipment_list.html', {'shipments': shipments})


def shipment_detail(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
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


def shipment_update(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            form.save()
            return redirect('shipment_detail', pk=pk)
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, 'shipment_form.html', {'form': form})


def shipment_delete(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    if request.method == 'POST':
        shipment.delete()
        return redirect('shipment_list')
    return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
