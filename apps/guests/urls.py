from django.urls import path
from . import views

app_name = 'guests'

urlpatterns = [
    path('', views.guest_list, name='guest_list'),
    path('<int:guest_id>/', views.guest_detail, name='guest_detail'),
    path('create/', views.create_guest, name='create_guest'),
    path('<int:guest_id>/edit/', views.edit_guest, name='edit_guest'),
    # path('<int:guest_id>/delete/', views.delete_guest, name='delete_guest'),
    path('search/', views.guest_search, name='guest_search'),
]
