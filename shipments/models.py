from django.utils import timezone

from django.db import models


class ShipmentStatus(models.Model):
    STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('PROCESSING', 'Processing'),
        ('PREPARATION', 'Preparation'),
        ('PICKUP', 'Pickup/Scheduling'),
        ('TRANSIT', 'Transit'),
        ('ARRIVAL', 'Arrival at Destination'),
        ('DELIVERED', 'Delivery'),
    ]

    shipment = models.ForeignKey('Shipment', related_name='statuses', on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.status} - {self.date_time}"


class Shipment(models.Model):
    """
    A model representing a shipment.

    Attributes:
        event (CharField): A description of the shipment event.
        merchant (PositiveIntegerField): The ID of the merchant associated with the shipment.
        created_at (DateTimeField): The date and time when the shipment was created.
        id (CharField): The unique identifier for the shipment.
        data (JSONField): Additional data related to the shipment.

    Indexes:
        - data: An index on the 'data' field for faster search queries.
        - event: An index on the 'event' field for faster search queries.

    Methods:
        - search_shipments(cls, query): A class method that searches for shipments based on a query in the 'data' field.

    """
    event = models.CharField(max_length=50, null=True, blank=True)
    merchant = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    id = models.PositiveIntegerField(primary_key=True, )
    data = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['data']),
            models.Index(fields=['event']),
        ]

    @classmethod
    def search_shipments(cls, query):
        """
        A class method that searches for shipments based on a query in the 'data' field.

        Args:
            query (str): The query string to search for in the 'data' field.

        Returns:
            QuerySet: A QuerySet of Shipment objects that match the query.

        Raises:
            ValueError: If the query is not a string.

        """
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")
        return cls.objects.filter(data__icontains=query)

    def __str__(self):
        """
        A string representation of the Shipment object.

        Returns:
            str: A string representation of the Shipment object, including its ID.

        """
        return f"Shipment {self.id}"
