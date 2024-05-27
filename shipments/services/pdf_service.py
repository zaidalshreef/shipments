from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from ..models import Shipment
import logging

logger = logging.getLogger(__name__)


def generate_pdf_label(request, shipment_id):
    """
    Generates a PDF label for a shipment.

    Args:
    shipment_id (int): The ID of the shipment.

    Returns:
    HttpResponse: The HTTP response containing the PDF label.
    """
    try:
        logger.info(f"Generating PDF label for shipment ID: {shipment_id}")
        shipment = Shipment.objects.get(shipment_id=shipment_id)
    except Shipment.DoesNotExist:
        logger.error(f"Shipment with ID {shipment_id} does not exist.")
        return JsonResponse({'error': 'Shipment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error retrieving shipment: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

    try:
        html_string = render_to_string('shipment_label.html', {'shipment': shipment})
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="shipment_label_{shipment_id}.pdf"'
        logger.info(f"PDF label generated successfully for shipment ID: {shipment_id}")
        return response
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
