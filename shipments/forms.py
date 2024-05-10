

from django import forms
from .models import Shipment


class ShipmentForm(forms.ModelForm):
    """
    A form class for handling Shipment model instances.

    Attributes:
        model: The Shipment model instance.
        fields: All fields of the Shipment model.

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
            fields: All fields of the Shipment model.
        """
        model = Shipment
        fields = '__all__'
