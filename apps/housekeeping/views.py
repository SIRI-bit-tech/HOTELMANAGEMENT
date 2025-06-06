from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import HousekeepingTask, HousekeepingSupply, MaintenanceRequest
from .forms import HousekeepingTaskForm, SupplyForm, MaintenanceRequestForm

@login_required
def task_list(request):
    """Display list of housekeeping tasks"""
    tasks = HousekeepingTask.objects.select_related('room', 'assigned_to').all()
    
    # Filtering
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    task_type = request.GET.get('task_type')
    assigned_to = request.GET.get('assigned_to')
    
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if task_type:
        tasks = tasks.filter(task_type=task_type)
    if assigned_to:
        tasks = tasks.filter(assigned_to_id=assigned_to)
    
    tasks = tasks.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tasks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'current_filters': {
            'status': status,
            'priority': priority,
            'task_type': task_type,
            'assigned_to': assigned_to,
        }
    }
    
    return render(request, 'housekeeping/task_list.html', context)

@login_required
def task_detail(request, task_id):
    """Display task details"""
    task = get_object_or_404(HousekeepingTask, id=task_id)
    
    context = {
        'task': task,
    }
    
    return render(request, 'housekeeping/task_detail.html', context)

@login_required
def create_task(request):
    """Create a new housekeeping task"""
    if request.method == 'POST':
        form = HousekeepingTaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task created successfully!')
            return redirect('housekeeping:task_detail', task_id=task.id)
    else:
        form = HousekeepingTaskForm()
    
    context = {'form': form, 'title': 'Create Task'}
    return render(request, 'housekeeping/task_form.html', context)

@login_required
def edit_task(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(HousekeepingTask, id=task_id)
    
    if request.method == 'POST':
        form = HousekeepingTaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('housekeeping:task_detail', task_id=task.id)
    else:
        form = HousekeepingTaskForm(instance=task)
    
    context = {'form': form, 'task': task, 'title': 'Edit Task'}
    return render(request, 'housekeeping/task_form.html', context)

@login_required
def complete_task(request, task_id):
    """Mark task as completed"""
    if request.method == 'POST':
        task = get_object_or_404(HousekeepingTask, id=task_id)
        task.mark_completed()  # Use the model method
        
        messages.success(request, 'Task marked as completed!')
        return redirect('housekeeping:task_detail', task_id=task.id)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def maintenance_list(request):
    """Display maintenance requests"""
    requests = MaintenanceRequest.objects.select_related('room').all()
    
    context = {
        'maintenance_requests': requests,
    }
    
    return render(request, 'housekeeping/maintenance_list.html', context)

@login_required
def supply_list(request):
    """Display supply inventory"""
    supplies = HousekeepingSupply.objects.all()  # Changed from Supply to HousekeepingSupply
    
    context = {
        'supplies': supplies,
    }
    
    return render(request, 'housekeeping/supply_list.html', context)