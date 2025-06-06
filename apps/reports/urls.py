from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('dashboard/', views.report_dashboard, name='dashboard'),
    path('occupancy/', views.occupancy_report, name='occupancy_report'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('guest-history/', views.guest_history_report, name='guest_history_report'),
]
