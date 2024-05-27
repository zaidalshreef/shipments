from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from ..models import Shipment
from asgiref.sync import sync_to_async


async def generate_pdf_label(request, shipment_id):
    """
    Generates a PDF label for a shipment.

    Args:
    shipment_id (int): The ID of the shipment.

    Returns:
    HttpResponse: The HTTP response containing the PDF label.
    """
    try:
        # Fetch shipment details asynchronously
        shipment = await sync_to_async(Shipment.objects.get)(shipment_id=shipment_id)

        # Render HTML to a string
        html_string = await sync_to_async(render_to_string)('shipment_label.html', {'shipment': shipment})

        # Generate PDF asynchronously
        html = HTML(string=html_string)
        pdf_file = await sync_to_async(html.write_pdf)()

        # Return PDF as an HTTP response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="shipment_label_{shipment_id}.pdf"'
        return response
    except Shipment.DoesNotExist:
        return HttpResponse('Shipment not found', status=404)
    except Exception as e:
        return HttpResponse(f'An error occurred: {e}', status=500)
