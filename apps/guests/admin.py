from django.contrib import admin
from django.utils.html import format_html
from .models import Guest, GuestDocument, GuestPreference


class GuestDocumentInline(admin.TabularInline):
    model = GuestDocument
    extra = 0
    fields = ['document_type', 'document_number', 'issue_date', 'expiry_date', 'file']


class GuestPreferenceInline(admin.StackedInline):
    model = GuestPreference
    extra = 0


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'nationality', 'is_vip', 'is_blacklisted', 'total_stays_display']
    list_filter = ['is_vip', 'is_blacklisted', 'gender', 'nationality', 'marketing_consent']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'id_number']
    list_editable = ['is_vip']
    inlines = [GuestDocumentInline, GuestPreferenceInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('title', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'nationality')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'alternate_phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Identification', {
            'fields': ('id_type', 'id_number', 'id_expiry_date')
        }),
        ('Preferences', {
            'fields': ('preferred_room_type', 'dietary_restrictions', 'special_requests')
        }),
        ('Marketing', {
            'fields': ('marketing_consent', 'newsletter_subscription')
        }),
        ('System Information', {
            'fields': ('is_vip', 'is_blacklisted', 'blacklist_reason', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def total_stays_display(self, obj):
        count = obj.get_total_stays()
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return count
    total_stays_display.short_description = 'Total Stays'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('reservations')


@admin.register(GuestDocument)
class GuestDocumentAdmin(admin.ModelAdmin):
    list_display = ['guest', 'document_type', 'document_number', 'issue_date', 'expiry_date']
    list_filter = ['document_type', 'issue_date', 'expiry_date']
    search_fields = ['guest__first_name', 'guest__last_name', 'document_number']
    date_hierarchy = 'expiry_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('guest')
