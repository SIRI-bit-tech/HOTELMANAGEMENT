from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('<int:room_id>/', views.room_detail, name='room_detail'),
    path('create/', views.create_room, name='create_room'),
    path('<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('availability/', views.availability_calendar, name='availability_calendar'),
    path('<int:room_id>/status-options/', views.room_status_options, name='room_status_options'),
    path('<int:room_id>/update-status/', views.update_room_status, name='update_room_status'),  # Add this
]
