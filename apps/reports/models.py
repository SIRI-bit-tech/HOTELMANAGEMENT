from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel


class ReportTemplate(TimeStampedModel):
    """Predefined report templates"""
    REPORT_TYPE_CHOICES = [
        ('occupancy', 'Occupancy Report'),
        ('revenue', 'Revenue Report'),
        ('guest', 'Guest Report'),
        ('housekeeping', 'Housekeeping Report'),
        ('maintenance', 'Maintenance Report'),
        ('financial', 'Financial Report'),
        ('custom', 'Custom Report'),
    ]

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(blank=True)

    # Report configuration
    query_config = models.JSONField(default=dict)  # Store query parameters
    chart_config = models.JSONField(default=dict)  # Store chart configuration

    # Access control
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_templates')

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['report_type', 'name']

    def __str__(self):
        return self.name


class GeneratedReport(TimeStampedModel):
    """Generated report instances"""
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')

    # Report parameters
    date_from = models.DateField()
    date_to = models.DateField()
    parameters = models.JSONField(default=dict)  # Additional parameters

    # Report data
    data = models.JSONField(default=dict)  # Cached report data
    file_path = models.CharField(max_length=500, blank=True)  # Path to generated file

    # Status
    is_cached = models.BooleanField(default=False)
    cache_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.date_from} to {self.date_to}"

    @property
    def is_cache_valid(self):
        """Check if cached data is still valid"""
        if not self.is_cached or not self.cache_expires_at:
            return False
        return timezone.now() < self.cache_expires_at


class ReportSchedule(TimeStampedModel):
    """Scheduled report generation"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)

    # Recipients
    email_recipients = models.TextField(help_text="Comma-separated email addresses")

    # Schedule settings
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField()
    last_run = models.DateTimeField(null=True, blank=True)

    # Additional settings
    parameters = models.JSONField(default=dict)

    class Meta:
        ordering = ['next_run']

    def __str__(self):
        return f"{self.name} ({self.frequency})"

