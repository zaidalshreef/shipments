# views.py or services/pdf_service.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from ..models import Shipment


def generate_pdf_label(request, shipment_id):
    """
    Generates a PDF label for a shipment.

    Args:
    shipment_id (int): The ID of the shipment.

    Returns:
    HttpResponse: The HTTP response containing the PDF label.
    """
    shipment = Shipment.objects.get(shipment_id=shipment_id)

    html_string = render_to_string('shipment_label.html', {'shipment': shipment})
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="shipment_label_{shipment_id}.pdf"'
    return response
