from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from apps.core.models import TimeStampedModel
from apps.guests.models import Guest
from apps.reservations.models import Reservation


class Invoice(TimeStampedModel):
    """Guest invoices and billing"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Basic invoice info
    invoice_number = models.CharField(max_length=20, unique=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='invoices')
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    
    # Dates
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and payment tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_date = models.DateField(null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issue_date', '-created_at']
        indexes = [
            models.Index(fields=['guest', 'issue_date']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['invoice_number']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.guest.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        if not self.due_date:
            # Default to 30 days from issue date
            from datetime import timedelta
            self.due_date = self.issue_date + timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        import random
        import string
        from datetime import datetime
        
        # Format: INV-YYYY-XXXXXX
        year = datetime.now().year
        while True:
            number = f"INV-{year}-{''.join(random.choices(string.digits, k=6))}"
            if not Invoice.objects.filter(invoice_number=number).exists():
                return number
    
    @property
    def balance_due(self):
        """Get remaining balance due"""
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return (
            self.status in ['pending', 'overdue'] and
            self.due_date < timezone.now().date()
        )
    
    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        line_items = self.line_items.all()
        self.subtotal = sum(item.total_amount for item in line_items)
        
        # Calculate tax (you might want to get this from hotel settings)
        tax_rate = Decimal('0.0875')  # 8.75% default
        self.tax_amount = self.subtotal * tax_rate
        
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()


class InvoiceLineItem(TimeStampedModel):
    """Individual line items on an invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Optional references
    service_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"


class Payment(TimeStampedModel):
    """Payment records"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
        ('mobile_payment', 'Mobile Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Payment info
    payment_number = models.CharField(max_length=20, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(default=timezone.now)
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Additional info
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['guest', 'payment_date']),
            models.Index(fields=['invoice', 'status']),
            models.Index(fields=['payment_number']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        super().save(*args, **kwargs)
    
    def generate_payment_number(self):
        """Generate unique payment number"""
        import random
        import string
        from datetime import datetime
        
        # Format: PAY-YYYY-XXXXXX
        year = datetime.now().year
        while True:
            number = f"PAY-{year}-{''.join(random.choices(string.digits, k=6))}"
            if not Payment.objects.filter(payment_number=number).exists():
                return number


class Refund(TimeStampedModel):
    """Refund records"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]
    
    # Refund info
    refund_number = models.CharField(max_length=20, unique=True)
    original_payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Processing info
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requested_refunds')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.refund_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.refund_number:
            self.refund_number = self.generate_refund_number()
        super().save(*args, **kwargs)
    
    def generate_refund_number(self):
        """Generate unique refund number"""
        import random
        import string
        from datetime import datetime
        
        # Format: REF-YYYY-XXXXXX
        year = datetime.now().year
        while True:
            number = f"REF-{year}-{''.join(random.choices(string.digits, k=6))}"
            if not Refund.objects.filter(refund_number=number).exists():
                return number


