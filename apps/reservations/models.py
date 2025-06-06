from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.core.models import TimeStampedModel
from apps.guests.models import Guest
from apps.rooms.models import Room, RoomType


class Reservation(TimeStampedModel):
    """Hotel reservation"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    BOOKING_SOURCE_CHOICES = [
        ('direct', 'Direct Booking'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('walk_in', 'Walk-in'),
        ('booking_com', 'Booking.com'),
        ('expedia', 'Expedia'),
        ('airbnb', 'Airbnb'),
        ('other_ota', 'Other OTA'),
        ('travel_agent', 'Travel Agent'),
        ('corporate', 'Corporate'),
    ]

    # Basic reservation info
    reservation_number = models.CharField(max_length=20, unique=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='reservations')
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the reservation")

    # Dates and occupancy
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    children = models.PositiveIntegerField(default=0)
    infants = models.PositiveIntegerField(default=0)

    # Pricing
    room_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_nights = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Booking details
    booking_source = models.CharField(max_length=20, choices=BOOKING_SOURCE_CHOICES, default='direct')
    booking_reference = models.CharField(max_length=100, blank=True)  # External booking reference
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmed_at = models.DateTimeField(null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    # Special requests and notes
    special_requests = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    # Payment
    deposit_required = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-check_in_date', '-created_at']
        indexes = [
            models.Index(fields=['guest', 'check_in_date']),
            models.Index(fields=['room', 'check_in_date']),
            models.Index(fields=['status', 'check_in_date']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['reservation_number']),
        ]

    def __str__(self):
        return f"Reservation {self.reservation_number} - {self.guest.display_name}"

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            self.reservation_number = self.generate_reservation_number()

        # Calculate total nights
        if self.check_in_date and self.check_out_date:
            self.total_nights = (self.check_out_date - self.check_in_date).days

        # Calculate amounts
        if self.room_rate and self.total_nights:
            self.subtotal = self.room_rate * self.total_nights
            # Add tax calculation here based on hotel settings
            self.total_amount = self.subtotal + self.tax_amount

        super().save(*args, **kwargs)

    def generate_reservation_number(self):
        """Generate unique reservation number"""
        import random
        import string

        while True:
            number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Reservation.objects.filter(reservation_number=number).exists():
                return number

    @property
    def duration_nights(self):
        """Get duration in nights"""
        return (self.check_out_date - self.check_in_date).days

    @property
    def total_guests(self):
        """Get total number of guests"""
        return self.adults + self.children + self.infants

    @property
    def is_active(self):
        """Check if reservation is currently active"""
        return self.status in ['confirmed', 'checked_in']

    @property
    def can_check_in(self):
        """Check if guest can check in"""
        today = timezone.now().date()
        return (
                self.status == 'confirmed' and
                self.check_in_date <= today and
                self.room is not None
        )

    @property
    def can_check_out(self):
        """Check if guest can check out"""
        return self.status == 'checked_in'

    def get_balance_due(self):
        """Get remaining balance due"""
        from apps.billing.models import Payment

        total_paid = Payment.objects.filter(
            reservation=self,
            status='completed'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        return self.total_amount - total_paid


class ReservationGuest(TimeStampedModel):
    """Additional guests in a reservation"""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='additional_guests')
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ['reservation', 'guest']

    def __str__(self):
        return f"{self.reservation.reservation_number} - {self.guest.display_name}"


class ReservationService(TimeStampedModel):
    """Additional services added to reservation"""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=200)
    service_description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    service_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['service_date', 'service_name']

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reservation.reservation_number} - {self.service_name}"


class ReservationNote(TimeStampedModel):
    """Notes and comments on reservations"""
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='reservation_notes')
    note = models.TextField()
    is_internal = models.BooleanField(default=True)  # Internal notes vs guest-visible
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.reservation.reservation_number}"
