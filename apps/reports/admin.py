from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import GeneratedReport, ReportSchedule


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['template', 'generated_by', 'date_from', 'date_to', 'is_cached']
    list_filter = ['template', 'is_cached']
    search_fields = ['template__name', 'generated_by__username']
    readonly_fields = ['created_at', 'updated_at', 'file_path']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reports-dashboard/', self.admin_site.admin_view(self.reports_dashboard), name='reports_dashboard'),
            path('occupancy-report/', self.admin_site.admin_view(self.occupancy_report), name='admin_occupancy_report'),
            path('revenue-report/', self.admin_site.admin_view(self.revenue_report), name='admin_revenue_report'),
        ]
        return custom_urls + urls
    
    def reports_dashboard(self, request):
        from .views import reports_dashboard
        return reports_dashboard(request)
    
    def occupancy_report(self, request):
        from .views import occupancy_report
        return occupancy_report(request)
    
    def revenue_report(self, request):
        from .views import revenue_report
        return revenue_report(request)


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_report_type', 'frequency', 'is_active', 'next_run']
    list_filter = ['frequency', 'is_active']  # removed 'report_type'
    search_fields = ['name']

    def get_report_type(self, obj):
        return obj.template.report_type
    get_report_type.short_description = 'Report Type'
