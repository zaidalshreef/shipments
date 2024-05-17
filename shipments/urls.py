# shipments/urls.py
from django.urls import path
from . import views

app_name = 'shipments'

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('home/', views.home, name='home'),
    path('webhook/', views.webhook_handler, name='shipment_history'),
    path('create/', views.shipment_create, name='shipment_create'),
    path('<int:id>/', views.shipment_detail, name='shipment_detail'),
    path('<int:id>/update/', views.shipment_update, name='shipment_update'),
    path('<int:id>/delete/', views.shipment_delete, name='shipment_delete'),

]
