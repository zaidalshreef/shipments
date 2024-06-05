from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShipmentForm, ShipmentStatusForm
from .models import Shipment, ShipmentStatus
from .services import update_salla_api, handle_status_update, handle_shipment_update, send_shipment_email
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import logging



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


def home(request):
    try:
        shipments = Shipment.objects.all()
        shipment_total = shipments.count()
        shipment_delivered = 0
        shipment_returnd = 0 
        shipment_canceled = 0
       
        for ship in shipments:
         logging.info(' Shipment cancelled counters %s{shipment_canceled} {ship.statuses.last().status}')
         if ship.statuses.last().status== 'delivered':
           shipment_delivered+=1
         elif ship.statuses.last().status== 'cancelled':
            shipment_canceled+=1
            logging.info(' Shipment cancelled counters %s{shipment_canceled} {ship.statuses.last().status}')
         elif ship.statuses.last().status== 'returned':
           shipment_returnd+=1
        if  request.method == 'GET':
          q = request.GET['q']
          # data = Data.objects.filter(last_name__icontains=q)
          multiple_q = Shipment.shipping_number = q
          data = Shipment.objects.filter(multiple_q)
        else:
          data = Shipment.shipping_number = '000004052024'
          context = {
          'data': data
            }
 
        return render(request, 'home.html',context,{'shipments':shipments ,'shipment_total':shipment_total, 'shipment_delivered':shipment_delivered, 'shipment_canceled':shipment_canceled})
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
                #handle_shipment_update(shipment)
                return redirect('shipment_detail', shipment_id=shipment_id)
        else:
            form = ShipmentForm(instance=shipment)
        return render(request, 'shipment_form.html', {'form': form, 'shipment': shipment})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


def update_status(request, shipment_id):
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
        return render(request, 'home.html', {'form': form, 'shipment': shipment})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)
        


def shipment_delete(request, shipment_id):
    try:
        shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
        if request.method == 'POST':
            shipment.delete()
            return redirect('shipment_list')
        return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)
