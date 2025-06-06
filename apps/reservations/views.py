from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Reservation
from .forms import ReservationForm, CheckInForm, CheckOutForm
from apps.rooms.models import Room
from apps.guests.models import Guest

@login_required
def reservation_list(request):
    """Display list of all reservations with filtering"""
    reservations = Reservation.objects.select_related('guest', 'room').all()
    
    # Filtering
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if status:
        reservations = reservations.filter(status=status)
    if date_from:
        reservations = reservations.filter(check_in_date__gte=date_from)
    if date_to:
        reservations = reservations.filter(check_out_date__lte=date_to)
    if search:
        reservations = reservations.filter(
            Q(guest__first_name__icontains=search) |
            Q(guest__last_name__icontains=search) |
            Q(room__room_number__icontains=search)
        )
    
    reservations = reservations.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reservations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reservations': page_obj,
        'current_filters': {
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
            'search': search,
        }
    }
    
    if request.htmx:
        return render(request, 'reservations/partials/reservation_list_partial.html', context)
    
    return render(request, 'reservations/reservation_list.html', context)

@login_required
def reservation_detail(request, reservation_id):
    """Display reservation details"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    context = {
        'reservation': reservation,
    }
    
    return render(request, 'reservations/reservation_detail.html', context)

@login_required
def create_reservation(request):
    """Create a new reservation"""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save()
            messages.success(request, f'Reservation created successfully for {reservation.guest.full_name}!')
            return redirect('reservations:reservation_detail', reservation_id=reservation.id)
    else:
        form = ReservationForm()
    
    context = {'form': form, 'title': 'Create Reservation'}
    return render(request, 'reservations/reservation_form.html', context)

@login_required
def edit_reservation(request, reservation_id):
    """Edit an existing reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            reservation = form.save()
            messages.success(request, f'Reservation updated successfully!')
            return redirect('reservations:reservation_detail', reservation_id=reservation.id)
    else:
        form = ReservationForm(instance=reservation)
    
    context = {'form': form, 'reservation': reservation, 'title': 'Edit Reservation'}
    return render(request, 'reservations/reservation_form.html', context)

@login_required
def cancel_reservation(request, reservation_id):
    """Cancel a reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        
        # Free up the room
        if reservation.room:
            reservation.room.status = 'available'
            reservation.room.save()
        
        messages.success(request, f'Reservation cancelled successfully!')
        return redirect('reservations:reservation_list')
    
    context = {'reservation': reservation}
    return render(request, 'reservations/cancel_reservation.html', context)

@login_required
def check_in(request, reservation_id):
    """Check in a guest"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        form = CheckInForm(request.POST, instance=reservation)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.status = 'checked_in'
            reservation.actual_check_in = timezone.now()
            reservation.save()
            
            # Update room status
            if reservation.room:
                reservation.room.status = 'occupied'
                reservation.room.save()
            
            messages.success(request, f'Guest {reservation.guest.full_name} checked in successfully!')
            return redirect('reservations:reservation_detail', reservation_id=reservation.id)
    else:
        form = CheckInForm(instance=reservation)
    
    context = {'form': form, 'reservation': reservation, 'title': 'Check In'}
    return render(request, 'reservations/check_in_form.html', context)

@login_required
def check_out(request, reservation_id):
    """Check out a guest"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        form = CheckOutForm(request.POST, instance=reservation)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.status = 'checked_out'
            reservation.actual_check_out = timezone.now()
            reservation.save()
            
            # Update room status
            if reservation.room:
                reservation.room.status = 'dirty'
                reservation.room.save()
                
                # Create housekeeping task
                from apps.housekeeping.models import HousekeepingTask
                HousekeepingTask.objects.create(
                    room=reservation.room,
                    task_type='cleaning',
                    description=f'Clean room {reservation.room.room_number} after checkout',
                    priority='normal',
                    status='pending'
                )
            
            messages.success(request, f'Guest {reservation.guest.full_name} checked out successfully!')
            return redirect('reservations:reservation_detail', reservation_id=reservation.id)
    else:
        form = CheckOutForm(instance=reservation)
    
    context = {'form': form, 'reservation': reservation, 'title': 'Check Out'}
    return render(request, 'reservations/check_out_form.html', context)

@login_required
def reservation_calendar(request):
    """Display reservation calendar"""
    from datetime import datetime, timedelta
    
    # Get date range
    start_date = request.GET.get('start_date')
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date()
    
    end_date = start_date + timedelta(days=30)
    
    # Get reservations for the period
    reservations = Reservation.objects.filter(
        check_in_date__lte=end_date,
        check_out_date__gte=start_date
    ).select_related('guest', 'room')
    
    # Get all rooms
    rooms = Room.objects.all().order_by('room_number')
    
    # Build calendar data
    calendar_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_data = {
            'date': current_date,
            'reservations': reservations.filter(
                check_in_date__lte=current_date,
                check_out_date__gt=current_date
            )
        }
        calendar_data.append(day_data)
        current_date += timedelta(days=1)
    
    context = {
        'calendar_data': calendar_data,
        'rooms': rooms,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'reservations/reservation_calendar.html', context)
