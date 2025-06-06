from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('', views.reservation_list, name='reservation_list'),
    path('<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('create/', views.create_reservation, name='create_reservation'),
    path('<int:reservation_id>/edit/', views.edit_reservation, name='edit_reservation'),
    path('<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('<int:reservation_id>/check-in/', views.check_in, name='check_in'),
    path('<int:reservation_id>/check-out/', views.check_out, name='check_out'),
    path('calendar/', views.reservation_calendar, name='reservation_calendar'),
]

