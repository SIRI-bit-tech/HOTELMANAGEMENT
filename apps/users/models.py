from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from apps.core.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    """Extended user profile"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('front_desk', 'Front Desk'),
        ('housekeeping', 'Housekeeping'),
        ('maintenance', 'Maintenance'),
        ('accounting', 'Accounting'),
        ('guest_services', 'Guest Services'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal info
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    
    # Work info
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='front_desk')
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    
    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    theme = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )
    
    # Permissions
    can_access_reports = models.BooleanField(default=False)
    can_manage_rates = models.BooleanField(default=False)
    can_process_payments = models.BooleanField(default=False)
    can_manage_housekeeping = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"
    
    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username


class UserSession(TimeStampedModel):
    """Track user sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
