from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Invoice, Payment, InvoiceLineItem
from .forms import InvoiceForm, PaymentForm

@login_required
def invoice_list(request):
    """Display list of invoices"""
    invoices = Invoice.objects.select_related('reservation__guest').all()
    
    # Filtering
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if status:
        invoices = invoices.filter(status=status)
    if date_from:
        invoices = invoices.filter(created_at__date__gte=date_from)
    if date_to:
        invoices = invoices.filter(created_at__date__lte=date_to)
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(reservation__guest__first_name__icontains=search) |
            Q(reservation__guest__last_name__icontains=search)
        )
    
    invoices = invoices.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'invoices': page_obj,
        'current_filters': {
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
        }
    }
    
    return render(request, 'billing/invoice_list.html', context)

@login_required
def invoice_detail(request, invoice_id):
    """Display invoice details"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    context = {
        'invoice': invoice,
    }
    
    return render(request, 'billing/invoice_detail.html', context)

@login_required
def create_invoice(request):
    """Create a new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully!')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    
    context = {'form': form, 'title': 'Create Invoice'}
    return render(request, 'billing/invoice_form.html', context)

@login_required
def payment_list(request):
    """Display list of payments"""
    payments = Payment.objects.select_related('invoice__reservation__guest').all()
    
    payments = payments.order_by('-payment_date')
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
    }
    
    return render(request, 'billing/payment_list.html', context)

@login_required
def create_payment(request):
    """Create a new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, 'Payment recorded successfully!')
            return redirect('billing:invoice_detail', invoice_id=payment.invoice.id)
    else:
        form = PaymentForm()
    
    context = {'form': form, 'title': 'Record Payment'}
    return render(request, 'billing/payment_form.html', context)
