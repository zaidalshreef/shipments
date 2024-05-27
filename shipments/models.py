import uuid
from django.utils import timezone
from django.db import models
from datetime import datetime


class ShipmentStatus(models.Model):
    """
    Model representing the status of a shipment.

    Attributes:
        shipment (ForeignKey): The shipment associated with this status.
        status (CharField): The current status of the shipment.
        date_time (DateTimeField): The date and time when the status was updated.

    Class Methods:
        None

    Instance Methods:
        __str__(self):
            Returns a string representation of the shipment status, e.g., "Shipment Status: Created - 2022-01-01 12:00:00".
    """
    STATUS_CHOICES = [
        ('creating', 'Creating'),
        ('created', 'Created'),
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('delivering', 'Delivering'),
        ('returned', 'Returned'),
        ('in_progress', 'In Progress'),
        ('cancelled', 'Cancelled'),
    ]

    shipment = models.ForeignKey('Shipment', related_name='statuses', on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        Returns a string representation of the shipment status, e.g., "Shipment Status: Created - 2022-01-01 12:00:00".

        Args:
            self: The instance of the ShipmentStatus model.

        Returns:
            str: A string representation of the shipment status.
        """
        return f"Shipment Status: {self.status} - {self.date_time}"


class Shipment(models.Model):
    """
    Model representing a shipment.

    Attributes:
        event (CharField): The event associated with the shipment.
        merchant (PositiveIntegerField): The unique identifier of the merchant.
        created_at (DateTimeField): The date and time when the shipment was created.
        shipment_id (PositiveIntegerField): The unique identifier of the shipment.
        type (CharField): The type of the shipment.
        shipping_number (UUIDField): A unique identifier for the shipment.
        courier_name (CharField): The name of the courier handling the shipment.
        courier_logo (URLField): The URL of the courier's logo.
        tracking_number (CharField): The tracking number associated with the shipment.
        tracking_link (URLField): The URL of the tracking page for the shipment.
        payment_method (CharField): The payment method used for the shipment.
        total (JSONField): The total cost of the shipment.
        cash_on_delivery (JSONField): The cash on delivery details for the shipment.
        label (JSONField): The label details for the shipment.
        total_weight (JSONField): The total weight of the shipment.
        created_at_details (JSONField): Additional details about the creation date and time of the shipment.
        packages (JSONField): The details of the packages in the shipment.
        ship_from (JSONField): The details of the shipment origin.
        ship_to (JSONField): The details of the shipment destination.
        meta (JSONField): Additional metadata for the shipment.

    Class Methods:
        search_shipments(cls, query):
            Searches shipments based on the provided query.

            Args:
                query (str): The query string to search for in shipping_number and tracking_number fields.

            Returns:
                QuerySet: A QuerySet of Shipment objects that match the query.

            Raises:
                ValueError: If the query is not a string.

    Instance Methods:
        __str__(self):
            Returns a string representation of the shipment, e.g., "Shipment 123".
    """
    event = models.CharField(max_length=50)
    merchant = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    shipment_id = models.PositiveIntegerField(primary_key=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    shipping_number = models.CharField(max_length=12, unique=True, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.shipping_number:
            self.shipping_number = self.generate_unique_shipping_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_shipping_number():
        now = datetime.now()
        month_year = now.strftime("%m%Y")

        # Find the highest current shipping number for the current month/year
        last_shipment = Shipment.objects.filter(created_at__year=now.year, created_at__month=now.month).order_by('shipping_number').last()

        if last_shipment and last_shipment.shipping_number:
            last_count = int(last_shipment.shipping_number[:6]) + 1
        else:
            last_count = 1

        shipping_number = f"{last_count:06d}{month_year}"
        return shipping_number

    class Meta:
        indexes = [
            models.Index(fields=['shipping_number']),
            models.Index(fields=['shipment_id']),
        ]

    @classmethod
    def search_shipments(cls, query):
        """
        Searches shipments based on the provided query.

        Args:
            query (str): The query string to search for in shipping_number and tracking_number fields.

        Returns:
            QuerySet: A QuerySet of Shipment objects that match the query.

        Raises:
            ValueError: If the query is not a string.
        """
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")
        return cls.objects.filter(
            models.Q(shipping_number__icontains=query) |
            models.Q(tracking_number__icontains=query)
        )

    def __str__(self):
        """
        Returns a string representation of the shipment, e.g., "Shipment 123".

        Args:
            self: The instance of the Shipment model.

        Returns:
            str: A string representation of the shipment.
        """
        return f"Shipment {self.shipment_id}"


class MerchantToken(models.Model):
    """
    Model representing a token for a merchant.

    Attributes:
        merchant_id (PositiveIntegerField): The unique identifier of the merchant.
        access_token (CharField): The access token for the merchant.
        refresh_token (CharField): The refresh token for the merchant.
        expires_at (DateTimeField): The expiration date and time of the token.

    Methods:
        is_expired(self): Checks if the token has expired.
        __str__(self): Returns a string representation of the token.
    """
    merchant_id = models.PositiveIntegerField(unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()

    def is_expired(self):
        """
        Checks if the token has expired.

        Args:
            self: The instance of the MerchantToken model.

        Returns:
            bool: True if the token has expired, False otherwise.
        """
        return self.expires_at <= timezone.now()

    def __str__(self):
        """
        Returns a string representation of the token.

        Args:
            self: The instance of the MerchantToken model.

        Returns:
            str: A string representation of the token, e.g., "Merchant 123".
        """
        return f"Merchant {self.merchant_id}"
