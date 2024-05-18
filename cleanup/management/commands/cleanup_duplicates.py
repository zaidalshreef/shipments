from django.core.management.base import BaseCommand
from shipments.models import Shipment
from collections import Counter


class Command(BaseCommand):
    help = 'Remove duplicate shipping numbers'

    def handle(self, *args, **kwargs):
        # Fetch all shipments
        shipments = Shipment.objects.all()
        shipping_numbers = [shipment.shipping_number for shipment in shipments]
        duplicates = [item for item, count in Counter(shipping_numbers).items() if count > 1]

        for dup in duplicates:
            shipments_with_dup = Shipment.objects.filter(shipping_number=dup)
            for shipment in shipments_with_dup[1:]:
                self.stdout.write(f'Deleting shipment {shipment.id} with duplicate shipping number {dup}')
                shipment.delete()

        self.stdout.write(self.style.SUCCESS('Successfully removed duplicate shipping numbers'))
