from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
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

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="shipment_label_{shipment_id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Shipment Label")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 100, "Sender's Information")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 120, f"Name: {shipment.ship_from['name']}")
    p.drawString(100, height - 140, f"Address: {shipment.ship_from['address_line']}")
    p.drawString(100, height - 160, f"City: {shipment.ship_from['city']}")
    p.drawString(100, height - 180, f"Country: {shipment.ship_from['country']}")
    p.drawString(100, height - 200, f"Phone: {shipment.ship_from['phone']}")
    p.drawString(100, height - 220, f"Email: {shipment.ship_from['email']}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 260, "Recipient's Information")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 280, f"Name: {shipment.ship_to['name']}")
    p.drawString(100, height - 300, f"Address: {shipment.ship_to['address_line']}")
    p.drawString(100, height - 320, f"City: {shipment.ship_to['city']}")
    p.drawString(100, height - 340, f"Country: {shipment.ship_to['country']}")
    p.drawString(100, height - 360, f"Phone: {shipment.ship_to['phone']}")
    p.drawString(100, height - 380, f"Email: {shipment.ship_to['email']}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, height - 420, "Shipment Details")
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 440, f"Tracking Number: {shipment.tracking_number}")
    p.drawString(100, height - 460, f"Tracking Link: {shipment.tracking_link}")
    p.drawString(100, height - 480, f"Total Weight: {shipment.total_weight['value']} {shipment.total_weight['units']}")
    p.drawString(100, height - 500, f"Total Cost: {shipment.total['amount']} {shipment.total['currency']}")
    p.drawString(100, height - 540, "Shipping Cost: 19 SAR")

    p.showPage()
    p.save()

    return response
