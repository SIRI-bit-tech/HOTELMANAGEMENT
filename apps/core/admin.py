from django.contrib import admin
from django.utils.html import format_html
from .models import HotelSettings, AuditLog


@admin.register(HotelSettings)
class HotelSettingsAdmin(admin.ModelAdmin):
    list_display = ['hotel_name', 'hotel_phone', 'hotel_email', 'currency', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('hotel_name', 'hotel_address', 'hotel_phone', 'hotel_email', 'hotel_website')
        }),
        ('Business Settings', {
            'fields': ('check_in_time', 'check_out_time', 'currency', 'tax_rate')
        }),
        ('Email Configuration', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_use_tls'),
            'classes': ('collapse',)
        }),
        ('Notifications', {
            'fields': ('enable_email_notifications', 'enable_sms_notifications')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not HotelSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'timestamp', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'object_repr', 'ip_address']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address', 'user_agent', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
