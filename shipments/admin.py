from django.contrib import admin
from .models import Shipment, ShipmentStatus, MerchantToken

admin.site.register(Shipment)
admin.site.register(ShipmentStatus)
admin.site.register(MerchantToken)
