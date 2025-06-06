from django.urls import path
from . import views

app_name = 'frontdesk'

urlpatterns = [
    path('', views.frontdesk_dashboard, name='dashboard'),
    path('room-status/', views.room_status_board, name='room_status_board'),
    path('check-in/<int:reservation_id>/', views.quick_check_in, name='quick_check_in'),
    path('check-out/<int:reservation_id>/', views.quick_check_out, name='quick_check_out'),
]
