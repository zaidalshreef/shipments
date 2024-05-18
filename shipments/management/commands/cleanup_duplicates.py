from django.core.management.base import BaseCommand
from django.db import models
from shipments.models import Shipment


class Command(BaseCommand):
    help = 'Cleanup duplicate shipments by shipping_number'

    def handle(self, *args, **kwargs):
        duplicates = (
            Shipment.objects.values('shipping_number')
            .annotate(count=models.Count('event'))
            .filter(count__gt=1)
        )

        for duplicate in duplicates:
            shipping_number = duplicate['shipping_number']
            shipments = Shipment.objects.filter(shipping_number=shipping_number)
            for shipment in shipments[1:]:
                shipment.delete()

        self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate shipments'))
