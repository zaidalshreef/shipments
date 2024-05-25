from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShipmentForm, ShipmentStatusForm
from .models import Shipment
from .services import update_salla_api, handle_status_update, handle_shipment_update
import os
from dotenv import load_dotenv

load_dotenv()

# Retrieve the Google Maps API key from the environment variables
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY','AIzaSyA6mmmEz_JCmb6p-yD6RnDPtRt7o4SXjh8' )


def home(request):
    shipments = Shipment.objects.all()

    return render(request, 'home.html', {'shipments': shipments})


def shipment_list(request):
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
        shipments = Shipment.objects.all()
    except Shipment.DoesNotExist:
        shipments = None

    return render(request, 'shipment_list.html', {'shipments': shipments})


def shipment_detail(request, shipment_id):
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
    context = {
        'shipment': shipment,
        'google_maps_api_key': GOOGLE_MAPS_API_KEY
    }
    return render(request, 'shipment_detail.html', context)


def update_shipment_details(request, shipment_id):
    """
    Update the details of a shipment.

    Args:
        request (HttpRequest): The HTTP request object.
        shipment_id (int): The unique identifier of the shipment to be updated.

    Returns:
        HttpResponseRedirect: A redirect to the shipment detail page after successful update.

    Raises:
        Http404: If the shipment with the given shipment_id does not exist.

    Purpose:
        This function handles the POST request for updating the details of a shipment. It retrieves the shipment object using the provided shipment_id, validates the form data, updates the details, and then redirects to the shipment detail page.

    Usage:
        To update the details of a shipment, call this function with the appropriate HttpRequest object and the shipment_id of the shipment to be updated.

    Example:
        from django.urls import reverse
        from .views import update_shipment_details

        def update_shipment(request, shipment_id):
            return update_shipment_details(request, shipment_id)

    """
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
    if request.method == 'POST':
        form = ShipmentForm(request.POST, instance=shipment)
        if form.is_valid():
            shipment = form.save()  # Save the form data to the instance
            handle_shipment_update(shipment)  # Pass the shipment instance to the handle_shipment_update function
            return redirect('shipment_detail', shipment_id=shipment_id)
    else:
        form = ShipmentForm(instance=shipment)
    return render(request, 'shipment_form.html', {'form': form, 'shipment': shipment})


def update_status(request, shipment_id):
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
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
    if request.method == 'POST':
        form = ShipmentStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            handle_status_update(shipment_id, status)  # Pass the status to the handle_status_update function
            return redirect('shipments:shipment_detail', shipment_id=shipment_id)
    else:
        form = ShipmentStatusForm()
    return render(request, 'update_status_form.html', {'form': form, 'shipment': shipment})


def shipment_delete(request, shipment_id):
    """
    Delete a shipment.

    Args:
        request (HttpRequest): The HTTP request object.
        shipment_id (int): The unique identifier of the shipment to be deleted.

    Returns:
        HttpResponseRedirect: A redirect to the shipment list page after successful deletion.

    Raises:
        Http404: If the shipment with the given shipment_id does not exist.

    Purpose:
        This function handles the POST request for deleting a shipment. It retrieves the shipment object using the provided shipment_id, and then deletes it. After successful deletion, it redirects to the shipment list page.

    Usage:
        To delete a shipment, call this function with the appropriate HttpRequest object and the shipment_id of the shipment to be deleted.

    Example:
        from django.urls import reverse
        from .views import shipment_delete

        def delete_shipment(request, shipment_id):
            return shipment_delete(request, shipment_id)

    """
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)
    if request.method == 'POST':
        shipment.delete()
        return redirect('shipment_list')
    return render(request, 'shipment_confirm_delete.html', {'shipment': shipment})
