from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShipmentForm, ShipmentStatusForm
from .models import Shipment, ShipmentStatus
from .services import update_salla_api, handle_status_update, handle_shipment_update, send_shipment_email
from django.conf import settings
from django.http import HttpResponse, JsonResponse


def custom_page_not_found_view(request, exception):
    return redirect('shipments:home')


def send_test_email_view(request):
    try:
        shipment_data = {
            'shipment_id': '123456',
            'ship_from': {'name': 'Sender Name', 'address_line': '123 Street', 'city': 'City', 'country': 'Country',
                          'phone': '1234567890', 'email': 'sender@example.com'},
            'ship_to': {'name': 'Recipient Name', 'address_line': '456 Avenue', 'city': 'City', 'country': 'Country',
                        'phone': '0987654321', 'email': 'recipient@example.com'}
        }
        status = 'created'
        send_shipment_email(shipment_data, status)
        return HttpResponse('Test email sent successfully!')
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


def home(request ,shipment_id):
    try:
        shipments = Shipment.objects.all()
        shipment_total = shipments.count()
        form = ShipmentStatusForm()


        if request.method == 'POST':
            form = ShipmentStatusForm(request.POST)
            if form.is_valid():
                status = form.cleaned_data['status']
                handle_status_update(shipment_id, status)
                return redirect('shipments:shipment_detail', shipment_id=shipment_id)
            
            else: 
                form = ShipmentStatusForm()
        return render(request, 'home.html', {'shipments': shipments ,'shipment_total':shipment_total, form:'form'})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


def shipment_list(request):
    try:
        shipments = Shipment.objects.all()
        return render(request, 'shipment_list.html', {'shipments': shipments})
    except Shipment.DoesNotExist:
        return render(request, 'shipment_list.html', {'shipments': None})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


def shipment_detail(request, shipment_id):
    try:
        shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
        context = {
            'shipment': shipment,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'shipment_detail.html', context)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


def update_shipment_details(request, shipment_id):
    try:
        shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
        if request.method == 'POST':
            form = ShipmentForm(request.POST, instance=shipment)
            if form.is_valid():
                shipment = form.save()
                handle_shipment_update(shipment)
                return redirect('shipment_detail', shipment_id=shipment_id)
        else:
            form = ShipmentForm(instance=shipment)
        return render(request, 'shipment_form.html', {'form': form, 'shipment': shipment})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


'''def update_status(request, shipment_id):
    try:
        shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
        if request.method == 'POST':
            form = ShipmentStatusForm(request.POST)
            if form.is_valid():
                status = form.cleaned_data['status']
                handle_status_update(shipment_id, status)
                return redirect('shipments:shipment_detail', shipment_id=shipment_id)
        else:
            form = ShipmentStatusForm()
        return render(request, 'update_status_form.html', {'form': form, 'shipment': shipment})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)
        '''


def shipment_delete(request, shipment_id):
    try:
        shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
        if request.method == 'POST':
            shipment.delete()
            return redirect('shipment_list')
        return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)
