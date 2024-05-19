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
        fields = ['tracking_link', 'tracking_number', 'label' , 'packages', 'ship_from', 'ship_to', 'meta' , 'total' , 'total_weight' , 'cash_on_delivery' , 'payment_method' , 'courier_name' , 'courier_logo' , 'type']


class ShipmentStatusForm(forms.ModelForm):
    """
    A form class for handling specific fields of the ShipmentStatus model instances.

    Attributes:
        model: The ShipmentStatus model instance.
        fields: Only the 'status' field is included for updating the ShipmentStatus model.

    Methods:
        __init__(self, *args, **kwargs): Initializes the ShipmentStatusForm with the provided arguments.
        clean(self): Validates and cleans the form data.
        is_valid(self): Checks if the form data is valid.
        save(self, commit=True): Saves the form data to the ShipmentStatus model instance.
    """

    class Meta:
        """
        Meta class for the ShipmentStatusForm.

        Attributes:
            model: The ShipmentStatus model instance.
            fields: Only the 'status' field is included for updating the ShipmentStatus model.
        """
        model = ShipmentStatus
        fields = ['status']  # Only include the status field
