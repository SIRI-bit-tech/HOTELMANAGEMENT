from django.db import models
from django.core.validators import RegexValidator
from apps.core.models import TimeStampedModel


class Guest(TimeStampedModel):
    """Guest information"""
    TITLE_CHOICES = [
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
        ('dr', 'Dr.'),
        ('prof', 'Prof.'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]

    # Personal Information
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    identification_type = models.CharField(max_length=50, blank=True)
    identification_number = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    state = models.CharField(max_length=100, blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    preferences = models.TextField(blank=True)

    # Contact Information
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17)
    alternate_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # Address Information
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Identification
    id_type = models.CharField(max_length=50, blank=True)  # Passport, Driver's License, etc.
    id_number = models.CharField(max_length=100, blank=True)
    id_expiry_date = models.DateField(null=True, blank=True)

    # Preferences
    preferred_room_type = models.CharField(max_length=100, blank=True)
    dietary_restrictions = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)

    # Marketing
    marketing_consent = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=False)

    # System fields
    is_vip = models.BooleanField(default=False)
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['is_vip']),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        parts = [self.title, self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, parts))

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts))

    def get_total_stays(self):
        """Get total number of completed stays"""
        return self.reservations.filter(status='checked_out').count()

    def get_total_spent(self):
        """Get total amount spent by guest"""
        from apps.billing.models import Invoice
        from django.db.models import Sum

        total = Invoice.objects.filter(
            guest=self,
            status='paid'
        ).aggregate(total=Sum('total_amount'))['total']

        return total or 0


class GuestDocument(TimeStampedModel):
    """Guest documents and attachments"""
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('drivers_license', 'Driver\'s License'),
        ('national_id', 'National ID'),
        ('visa', 'Visa'),
        ('other', 'Other'),
    ]

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issuing_authority = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='guest_documents/')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.guest.display_name} - {self.get_document_type_display()}"


class GuestPreference(TimeStampedModel):
    """Guest preferences and special requirements"""
    guest = models.OneToOneField(Guest, on_delete=models.CASCADE, related_name='guest_preferences')

    # Room preferences
    preferred_floor = models.CharField(max_length=20, blank=True)
    preferred_view = models.CharField(max_length=100, blank=True)
    smoking_preference = models.CharField(
        max_length=20,
        choices=[('smoking', 'Smoking'), ('non_smoking', 'Non-Smoking')],
        default='non_smoking'
    )

    # Service preferences
    housekeeping_frequency = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('every_other_day', 'Every Other Day'), ('weekly', 'Weekly')],
        default='daily'
    )
    wake_up_call = models.BooleanField(default=False)
    newspaper_delivery = models.BooleanField(default=False)

    # Accessibility needs
    wheelchair_accessible = models.BooleanField(default=False)
    hearing_impaired = models.BooleanField(default=False)
    visually_impaired = models.BooleanField(default=False)
    other_accessibility_needs = models.TextField(blank=True)

    def __str__(self):
        return f"{self.guest.display_name} - Preferences"
