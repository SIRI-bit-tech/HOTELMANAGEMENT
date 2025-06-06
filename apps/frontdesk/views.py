from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from apps.reservations.models import Reservation
from apps.rooms.models import Room
from apps.guests.models import Guest
from apps.housekeeping.models import HousekeepingTask

@login_required
def frontdesk_dashboard(request):
    today = timezone.now().date()
    
    # Today's arrivals
    arrivals = Reservation.objects.filter(
        check_in_date=today,
        status='confirmed'
    ).select_related('guest', 'room')
    
    # Today's departures
    departures = Reservation.objects.filter(
        check_out_date=today,
        status='checked_in'
    ).select_related('guest', 'room')
    
    # Current occupancy
    occupied_rooms = Room.objects.filter(status='occupied').count()
    total_rooms = Room.objects.count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Pending housekeeping tasks
    pending_tasks = HousekeepingTask.objects.filter(
        status='pending'
    ).count()
    
    context = {
        'arrivals': arrivals,
        'departures': departures,
        'occupied_rooms': occupied_rooms,
        'total_rooms': total_rooms,
        'occupancy_rate': occupancy_rate,
        'pending_tasks': pending_tasks,
    }
    
    return render(request, 'frontdesk/dashboard.html', context)

@login_required
def room_status_board(request):
    rooms = Room.objects.select_related('room_type').prefetch_related(
        'reservation_set'
    ).order_by('number')
    
    if request.htmx:
        return render(request, 'frontdesk/partials/room_status_partial.html', {
            'rooms': rooms,
        })
    
    return render(request, 'frontdesk/room_status_board.html', {
        'rooms': rooms,
    })

@login_required
def quick_check_in(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.status = 'checked_in'
        reservation.actual_check_in = timezone.now()
        reservation.save()
        
        reservation.room.status = 'occupied'
        reservation.room.save()
        
        messages.success(request, f'Guest {reservation.guest.full_name} checked in successfully!')
        
        if request.htmx:
            return render(request, 'frontdesk/partials/check_in_success.html', {
                'reservation': reservation,
            })
        
        return redirect('frontdesk:dashboard')
    
    return render(request, 'frontdesk/quick_check_in.html', {
        'reservation': reservation,
    })

@login_required
def quick_check_out(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.status = 'checked_out'
        reservation.actual_check_out = timezone.now()
        reservation.save()
        
        reservation.room.status = 'dirty'
        reservation.room.save()
        
        # Create housekeeping task
        HousekeepingTask.objects.create(
            room=reservation.room,
            task_type='cleaning',
            description=f'Clean room after checkout - Guest: {reservation.guest.full_name}',
            priority='high',
            assigned_to=None,
            status='pending'
        )
        
        messages.success(request, f'Guest {reservation.guest.full_name} checked out successfully!')
        
        if request.htmx:
            return render(request, 'frontdesk/partials/check_out_success.html', {
                'reservation': reservation,
            })
        
        return redirect('frontdesk:dashboard')
    
    return render(request, 'frontdesk/quick_check_out.html', {
        'reservation': reservation,
    })
