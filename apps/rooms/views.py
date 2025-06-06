from django.utils import timezone  # Fixed import
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Room, RoomType
from .forms import RoomForm, RoomTypeForm

@login_required
def room_list(request):
    """Display list of all rooms with filtering"""
    rooms = Room.objects.select_related('room_type').all()
    
    # Filtering
    room_type = request.GET.get('room_type')
    status = request.GET.get('status')
    floor = request.GET.get('floor')
    search = request.GET.get('search')
    
    if room_type:
        rooms = rooms.filter(room_type_id=room_type)
    if status:
        rooms = rooms.filter(status=status)
    if floor:
        rooms = rooms.filter(floor=floor)
    if search:
        rooms = rooms.filter(
            Q(number__icontains=search) |  # Fixed field name
            Q(room_type__name__icontains=search)
        )
    
    # Get filter options
    room_types = RoomType.objects.all()
    floors = Room.objects.values_list('floor', flat=True).distinct().order_by('floor')
    
    # Pagination
    paginator = Paginator(rooms, 24)  # 24 rooms per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'rooms': page_obj,
        'room_types': room_types,
        'floors': floors,
        'current_filters': {
            'room_type': room_type,
            'status': status,
            'floor': floor,
            'search': search,
        }
    }
    
    if request.htmx:
        return render(request, 'rooms/partials/room_list_partial.html', context)
    
    return render(request, 'rooms/room_list.html', context)

@login_required
def room_detail(request, room_id):
    """Display room details"""
    room = get_object_or_404(Room, id=room_id)
    
    # Get current and upcoming reservations
    current_reservation = room.reservations.filter(
        status='checked_in'
    ).first()
    
    upcoming_reservations = room.reservations.filter(
        status='confirmed',
        check_in_date__gte=timezone.now().date()
    ).order_by('check_in_date')[:5]
    
    # Get maintenance history
    maintenance_tasks = room.housekeeping_tasks.filter(
        task_type='maintenance'
    ).order_by('-created_at')[:10]
    
    context = {
        'room': room,
        'current_reservation': current_reservation,
        'upcoming_reservations': upcoming_reservations,
        'maintenance_tasks': maintenance_tasks,
    }
    
    return render(request, 'rooms/room_detail.html', context)

@login_required
def create_room(request):
    """Create a new room"""
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room {room.number} created successfully!')  # Fixed field name
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm()
    
    context = {'form': form, 'title': 'Create Room'}
    return render(request, 'rooms/room_form.html', context)

@login_required
def edit_room(request, room_id):
    """Edit an existing room"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room {room.number} updated successfully!')  # Fixed field name
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm(instance=room)
    
    context = {'form': form, 'room': room, 'title': 'Edit Room'}
    return render(request, 'rooms/room_form.html', context)

@login_required
def delete_room(request, room_id):
    """Delete a room"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room_number = room.number  # Store for success message
        room.delete()
        messages.success(request, f'Room {room_number} deleted successfully!')
        return redirect('rooms:room_list')
    
    context = {'room': room}
    return render(request, 'rooms/confirm_delete.html', context)

@login_required
def update_room_status(request, room_id):
    """Update room status via HTMX"""
    if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Room.ROOM_STATUS_CHOICES):  # Fixed constant name
            room.status = new_status
            room.save()
            
            # Create housekeeping task if needed
            if new_status == 'cleaning':  # Changed from 'dirty' to 'cleaning'
                from apps.housekeeping.models import HousekeepingTask
                HousekeepingTask.objects.create(
                    room=room,
                    task_type='cleaning',
                    description=f'Clean room {room.number}',  # Fixed field name
                    priority='normal',
                    assigned_to=None,
                    status='pending'
                )
        
        return render(request, 'rooms/partials/room_card.html', {'room': room})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def room_status_options(request, room_id):
    """Return status options for a room"""
    room = get_object_or_404(Room, id=room_id)
    status_choices = Room.ROOM_STATUS_CHOICES  # Fixed constant name
    
    context = {
        'room': room,
        'status_choices': status_choices
    }
    
    return render(request, 'rooms/partials/room_status_options.html', context)

@login_required
def availability_calendar(request):
    """Display room availability calendar"""
    from datetime import datetime, timedelta
    
    # Get date range (default to current month)
    start_date = request.GET.get('start_date')
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date().replace(day=1)
    
    end_date = start_date + timedelta(days=30)
    
    # Get all rooms and their reservations for the period
    rooms = Room.objects.all().order_by('number')  # Fixed field name
    
    calendar_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_data = {
            'date': current_date,
            'rooms': []
        }
        
        for room in rooms:
            reservation = room.reservations.filter(
                check_in_date__lte=current_date,
                check_out_date__gt=current_date,
                status__in=['confirmed', 'checked_in']
            ).first()
            
            day_data['rooms'].append({
                'room': room,
                'reservation': reservation,
                'available': not reservation
            })
        
        calendar_data.append(day_data)
        current_date += timedelta(days=1)
    
    context = {
        'calendar_data': calendar_data,
        'start_date': start_date,
        'end_date': end_date,
        'rooms': rooms
    }
    
    return render(request, 'rooms/availability_calendar.html', context)