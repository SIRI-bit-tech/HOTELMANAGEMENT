from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.rooms.models import Room

# Get the User model
User = settings.AUTH_USER_MODEL


class HousekeepingTask(TimeStampedModel):
    """Housekeeping tasks and room maintenance"""
    TASK_TYPE_CHOICES = [
        ('cleaning', 'Room Cleaning'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Room Inspection'),
        ('deep_clean', 'Deep Cleaning'),
        ('checkout_clean', 'Checkout Cleaning'),
        ('checkin_prep', 'Check-in Preparation'),
        ('laundry', 'Laundry'),
        ('amenity_restock', 'Amenity Restocking'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Basic task info
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='housekeeping_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Assignment and scheduling
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_tasks')
    scheduled_date = models.DateField(default=timezone.now)
    scheduled_time = models.TimeField(null=True, blank=True)
    estimated_duration = models.DurationField(null=True, blank=True)  # Expected time to complete

    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')

    # Completion tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    actual_duration = models.DurationField(null=True, blank=True)

    # Quality control
    quality_score = models.PositiveIntegerField(null=True, blank=True)  # 1-10 rating
    quality_notes = models.TextField(blank=True)
    inspected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='inspected_tasks')
    inspected_at = models.DateTimeField(null=True, blank=True)

    # Additional info
    notes = models.TextField(blank=True)
    requires_maintenance = models.BooleanField(default=False)
    maintenance_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-priority', 'scheduled_date', 'scheduled_time']
        indexes = [
            models.Index(fields=['room', 'scheduled_date']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['task_type', 'scheduled_date']),
        ]

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.room.number}"

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False

        now = timezone.now()
        scheduled_datetime = timezone.datetime.combine(
            self.scheduled_date,
            self.scheduled_time or timezone.datetime.min.time()
        )
        scheduled_datetime = timezone.make_aware(scheduled_datetime)

        return now > scheduled_datetime

    def mark_started(self, user=None):
        """Mark task as started"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        if user:
            self.assigned_to = user
        self.save()

    def mark_completed(self, user=None, notes=None):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()

        if self.started_at:
            self.actual_duration = self.completed_at - self.started_at

        if notes:
            self.notes = notes

        self.save()

        # Update room status if it's a cleaning task
        if self.task_type in ['cleaning', 'checkout_clean', 'checkin_prep']:
            self.room.status = 'available'
            self.room.save()


class HousekeepingSupply(TimeStampedModel):
    """Housekeeping supplies and inventory"""
    CATEGORY_CHOICES = [
        ('cleaning', 'Cleaning Supplies'),
        ('amenities', 'Guest Amenities'),
        ('linens', 'Linens & Towels'),
        ('maintenance', 'Maintenance Supplies'),
        ('equipment', 'Equipment'),
    ]

    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('bottle', 'Bottle'),
        ('pack', 'Pack'),
        ('roll', 'Roll'),
        ('liter', 'Liter'),
        ('kg', 'Kilogram'),
        ('set', 'Set'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    # Inventory tracking
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=10)
    maximum_stock = models.PositiveIntegerField(default=100)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')

    # Pricing
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    supplier_contact = models.CharField(max_length=200, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = "Housekeeping Supplies"

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"

    @property
    def is_low_stock(self):
        """Check if supply is running low"""
        return self.current_stock <= self.minimum_stock

    @property
    def stock_status(self):
        """Get stock status"""
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'


class HousekeepingSchedule(TimeStampedModel):
    """Staff scheduling for housekeeping"""
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='housekeeping_schedules')
    date = models.DateField()
    shift_start = models.TimeField()
    shift_end = models.TimeField()

    # Room assignments
    assigned_rooms = models.ManyToManyField(Room, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['staff_member', 'date']
        ordering = ['date', 'shift_start']

    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.date}"

    @property
    def shift_duration(self):
        """Calculate shift duration"""
        from datetime import datetime, timedelta

        start = datetime.combine(self.date, self.shift_start)
        end = datetime.combine(self.date, self.shift_end)

        # Handle overnight shifts
        if end < start:
            end += timedelta(days=1)

        return end - start


class MaintenanceRequest(TimeStampedModel):
    """Maintenance requests for rooms and facilities"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='maintenance_assignments')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Tracking
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reported_maintenance')
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.room.number} - {self.title}"
