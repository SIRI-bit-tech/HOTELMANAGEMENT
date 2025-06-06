from django.urls import path
from . import views

app_name = 'housekeeping'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('supplies/', views.supply_list, name='supply_list'),
]
