from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShipmentForm, ShipmentStatusForm
from .models import Shipment
from .services import update_salla_api, handle_status_update, handle_shipment_update
from django.conf import settings
from django.http import HttpResponse
from .services import send_shipment_email
from asgiref.sync import sync_to_async


async def send_test_email_view(request):
    shipment_data = {
        'shipment_id': '123456',
        'ship_from': {'name': 'Sender Name', 'address_line': '123 Street', 'city': 'City', 'country': 'Country',
                      'phone': '1234567890', 'email': 'sender@example.com'},
        'ship_to': {'name': 'Recipient Name', 'address_line': '456 Avenue', 'city': 'City', 'country': 'Country',
                    'phone': '0987654321', 'email': 'recipient@example.com'}
    }
    status = 'created'
    await send_shipment_email(shipment_data, status)
    return HttpResponse('Test email sent successfully!')


async def home(request):
    shipments = await sync_to_async(Shipment.objects.all)()
    return render(request, 'home.html', {'shipments': shipments})


async def shipment_list(request):
    """
    Retrieve all shipments and render the shipment list page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: An HTTP response containing the rendered shipment list page.

    Raises:
        Shipment.DoesNotExist: If there are no shipments in the database.

    Purpose:
        This function retrieves all shipments from the database and renders the shipment list page with the retrieved shipments. If there are no shipments in the database, it raises a Shipment.DoesNotExist exception.

    Usage:
        To render the shipment list page, call this function with the appropriate HttpRequest object.

    Example:
        from django.urls import reverse
        from .views import shipment_list

        def list_shipments(request):
            return shipment_list(request)

    """
    try:
        shipments = await sync_to_async(Shipment.objects.all)()
    except Shipment.DoesNotExist:
        shipments = None

    return render(request, 'shipment_list.html', {'shipments': shipments})


async def shipment_detail(request, shipment_id):
    shipment = await sync_to_async(get_object_or_404)(Shipment, shipment_id=shipment_id)
    context = {
        'shipment': shipment,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'shipment_detail.html', context)


async def update_shipment_details(request, shipment_id):
    shipment = await sync_to_async(get_object_or_404)(Shipment, shipment_id=shipment_id)
    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            shipment = await sync_to_async(form.save)()
            await handle_shipment_update(shipment)
            return redirect('shipments:shipment_detail', shipment_id=shipment_id)
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, 'shipment_form.html', {'form': form, 'shipment': shipment})


async def update_status(request, shipment_id):
    """
    Update the status of a shipment.

    Args:
        request (HttpRequest): The HTTP request object.
        shipment_id (int): The unique identifier of the shipment to be updated.

    Returns:
        HttpResponseRedirect: A redirect to the shipment detail page after successful status update.

    Raises:
        Http404: If the shipment with the given shipment_id does not exist.

    Purpose:
        This function handles the POST request for updating the status of a shipment. It retrieves the shipment object using the provided shipment_id, validates the form data, updates the status, and then redirects to the shipment detail page.

    Usage:
        To update the status of a shipment, call this function with the appropriate HttpRequest object and the shipment_id of the shipment to be updated.

    Example:
        from django.urls import reverse
        from .views import update_status

        def update_shipment_status(request, shipment_id):
            return update_status(request, shipment_id)

    """
    shipment = await sync_to_async(get_object_or_404)(Shipment, shipment_id=shipment_id)
    if request.method == 'POST':
        form = ShipmentStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            await handle_status_update(shipment_id, status)  # Pass the status to the handle_status_update function
            return redirect('shipments:shipment_detail', shipment_id=shipment_id)
    else:
        form = ShipmentStatusForm()
    return render(request, 'update_status_form.html', {'form': form, 'shipment': shipment})


async def shipment_delete(request, shipment_id):
    shipment = await sync_to_async(get_object_or_404)(Shipment, shipment_id=shipment_id)
    if request.method == 'POST':
        await sync_to_async(shipment.delete)()
        return redirect('shipments:shipment_list')
    return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
