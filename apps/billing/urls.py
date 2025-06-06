from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.create_payment, name='create_payment'),
]
