# shipments/urls.py
from django.urls import path, re_path
from . import views
from .services.webhook_service import webhook_handler
from .services.pdf_service import generate_pdf_label

app_name = 'shipments'

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('home/', views.home, name='home'),
    path('analytic/', views.analytic, name='analytic'),
    path('webhook/', webhook_handler, name='shipment_webhook'),
    path('send-test-email/', views.send_test_email_view, name='send_test_email'),
    path('generate-pdf-label/<int:shipment_id>/', generate_pdf_label, name='generate_pdf_label'),
    path('<int:shipment_id>/', views.shipment_detail, name='shipment_detail'),
    path('<int:shipment_id>/update/', views.update_shipment_details, name='shipment_update'),
    path('<int:shipment_id>/status/', views.update_status, name='update_status'),
    path('<int:shipment_id>/delete/', views.shipment_delete, name='shipment_delete'),

]

# Catch-all pattern to redirect any unmatched URLs to the home page
urlpatterns += [re_path(r'^.*$', lambda request: redirect('shipments:home'))]
