from .models import Shipment, ShipmentStatus
from django import forms


class ShipmentForm(forms.ModelForm):
    """
    A form class for handling specific fields of the Shipment model instances.

    Attributes:
        model: The Shipment model instance.
        fields: Only the fields specified for updating the Shipment model.

    Methods:
        __init__(self, *args, **kwargs): Initializes the ShipmentForm with the provided arguments.
        clean(self): Validates and cleans the form data.
        is_valid(self): Checks if the form data is valid.
        save(self, commit=True): Saves the form data to the Shipment model instance.
    """

    class Meta:
        """
        Meta class for the ShipmentForm.

        Attributes:
            model: The Shipment model instance.
            fields: Specific fields of the Shipment model.
        """
        model = Shipment
        fields = ['tracking_link', 'tracking_number', 'pdf_label']


class ShipmentStatusForm(forms.ModelForm):
    class Meta:
        model = ShipmentStatus
        fields = ['status']  # Only include the status field
