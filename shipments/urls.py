# shipments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('webhook/', views.webhook_handler, name='shipment_history'),
    path('create/', views.shipment_create, name='shipment_create'),
    path('<str:shipping_number>/', views.shipment_detail, name='shipment_detail'),
    path('<str:shipping_number>/update/', views.shipment_update, name='shipment_update'),
    path('<str:shipping_number>/delete/', views.shipment_delete, name='shipment_delete'),

]
