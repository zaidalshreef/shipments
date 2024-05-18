# shipments/urls.py
from django.urls import path
from . import views
from .services import webhook_handler

app_name = 'shipments'

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('home/', views.home, name='home'),
    path('webhook/', webhook_handler, name='shipment_webhook'),
    path('<int:id>/', views.shipment_detail, name='shipment_detail'),
    path('<int:id>/update/', views.update_shipment_details, name='shipment_update'),
    path('<int:id>/status/', views.update_status, name='update_status'),
    path('<int:id>/delete/', views.shipment_delete, name='shipment_delete'),

]
