import uuid

from django.utils import timezone
from django.db import models


class ShipmentStatus(models.Model):
    STATUS_CHOICES = [
        ('CREATING', 'Creating'),
        ('CREATED', 'Created'),
        ('PENDING', 'Pending'),
        ('DELIVERED', 'Delivered'),
        ('DELIVERING', 'Delivering'),
        ('RETURNED', 'Returned'),
        ('IN_PROGRESS', 'In Progress'),
        ('CANCELLED', 'Cancelled'),
    ]

    shipment = models.ForeignKey('Shipment', related_name='statuses', on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.status} - {self.date_time}"


class Shipment(models.Model):
    event = models.CharField(max_length=50)
    merchant = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    shipment_id = models.PositiveIntegerField(primary_key=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    shipping_number = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False)
    courier_name = models.CharField(max_length=100, null=True, blank=True)
    courier_logo = models.URLField(max_length=200, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    tracking_link = models.URLField(max_length=200, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    total = models.JSONField(null=True, blank=True)
    cash_on_delivery = models.JSONField(null=True, blank=True)
    label = models.JSONField(null=True, blank=True)
    total_weight = models.JSONField(null=True, blank=True)
    created_at_details = models.JSONField(null=True, blank=True)
    packages = models.JSONField(null=True, blank=True)
    ship_from = models.JSONField(null=True, blank=True)
    ship_to = models.JSONField(null=True, blank=True)
    meta = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['shipping_number']),
            models.Index(fields=['type']),
        ]

    @classmethod
    def search_shipments(cls, query):
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")
        return cls.objects.filter(
            models.Q(shipping_number__icontains=query) |
            models.Q(tracking_number__icontains=query)
        )

    def __str__(self):
        return f"Shipment {self.shipment_id}"
