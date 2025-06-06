from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Q
from apps.rooms.models import Room
from apps.reservations.models import Reservation
from apps.housekeeping.models import HousekeepingTask
from apps.guests.models import Guest
from apps.billing.models import Payment

def landing_page(request):
    """Landing page with parallax scrolling and SEO optimization"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    context = {
        'page_title': 'HotelPMS - Revolutionary Hotel Property Management System',
        'meta_description': 'Transform your hotel operations with HotelPMS - the most advanced property management system designed for modern hotels.',
    }
    return render(request, 'core/landing_page.html', context)

def about(request):
    """About page"""
    context = {
        'page_title': 'About HotelPMS - Leading Hotel Management Software',
        'meta_description': 'Learn about HotelPMS and how we\'re revolutionizing hotel property management with cutting-edge technology.',
    }
    return render(request, 'core/about.html', context)

def contact(request):
    """Contact page"""
    context = {
        'page_title': 'Contact HotelPMS - Get Expert Support',
        'meta_description': 'Contact our expert team for demos, support, and questions about HotelPMS hotel management software.',
    }
    return render(request, 'core/contact.html', context)

def features(request):
    """Features page"""
    context = {
        'page_title': 'HotelPMS Features - Complete Hotel Management Solution',
        'meta_description': 'Explore comprehensive features of HotelPMS including reservations, guest management, housekeeping, billing, and analytics.',
    }
    return render(request, 'core/features.html', context)

@login_required
def dashboard(request):
    """Enhanced dashboard with comprehensive metrics"""
    today = timezone.now().date()
    
    # Room statistics
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    maintenance_rooms = Room.objects.filter(status__in=['maintenance', 'out_of_order']).count()
    dirty_rooms = Room.objects.filter(status='dirty').count()
    
    # Calculate occupancy rate
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Reservation statistics
    arrivals_today = Reservation.objects.filter(
        check_in_date=today, 
        status='confirmed'
    ).count()
    
    departures_today = Reservation.objects.filter(
        check_out_date=today, 
        status='checked_in'
    ).count()
    
    stay_overs = Reservation.objects.filter(
        check_in_date__lt=today, 
        check_out_date__gt=today, 
        status='checked_in'
    ).count()
    
    # Revenue statistics
    today_revenue = Payment.objects.filter(
        payment_date__date=today,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_revenue = Payment.objects.filter(
        payment_date__month=today.month,
        payment_date__year=today.year,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Housekeeping statistics
    pending_tasks = HousekeepingTask.objects.filter(status='pending').count()
    urgent_tasks = HousekeepingTask.objects.filter(
        priority='urgent', 
        status__in=['pending', 'in_progress']
    ).count()
    
    # Guest statistics
    total_guests = Guest.objects.count()
    vip_guests = Guest.objects.filter(is_vip=True).count()
    
    # Recent activity
    recent_check_ins = Reservation.objects.filter(
        status='checked_in'
    ).order_by('-updated_at')[:5]
    
    recent_check_outs = Reservation.objects.filter(
        status='checked_out'
    ).order_by('-updated_at')[:5]
    
    # Upcoming arrivals
    upcoming_arrivals = Reservation.objects.filter(
        check_in_date=today,
        status='confirmed'
    ).order_by('check_in_date')[:10]
    
    # Room status distribution for chart
    room_status_data = Room.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'dirty_rooms': dirty_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
        'arrivals_today': arrivals_today,
        'departures_today': departures_today,
        'stay_overs': stay_overs,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'pending_tasks': pending_tasks,
        'urgent_tasks': urgent_tasks,
        'total_guests': total_guests,
        'vip_guests': vip_guests,
        'recent_check_ins': recent_check_ins,
        'recent_check_outs': recent_check_outs,
        'upcoming_arrivals': upcoming_arrivals,
        'room_status_data': room_status_data,
        'today': today,
    }
    
    return render(request, 'core/dashboard.html', context)
