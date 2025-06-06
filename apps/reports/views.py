from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from apps.reservations.models import Reservation
from apps.rooms.models import Room
from apps.billing.models import Payment
from apps.guests.models import Guest

@login_required
def report_list(request):
    """List all available reports"""
    reports = [
        {
            'name': 'Occupancy Report',
            'description': 'View room occupancy rates and trends',
            'url': 'reports:occupancy_report',
            'icon': 'bed'
        },
        {
            'name': 'Revenue Report', 
            'description': 'Analyze revenue and payment trends',
            'url': 'reports:revenue_report',
            'icon': 'dollar-sign'
        },
        {
            'name': 'Guest History Report',
            'description': 'Guest statistics and history analysis', 
            'url': 'reports:guest_history_report',
            'icon': 'users'
        }
    ]
    
    context = {
        'reports': reports,
        'title': 'Reports'
    }
    return render(request, 'reports/report_list.html', context)

@login_required
def report_dashboard(request):
    """Main reports dashboard"""
    context = {
        'title': 'Reports Dashboard'
    }
    return render(request, 'reports/dashboard.html', context)

@login_required
def occupancy_report(request):
    """Generate occupancy report"""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate occupancy data
    total_rooms = Room.objects.count()
    
    occupancy_data = []
    current_date = start_date
    
    while current_date <= end_date:
        occupied_rooms = Reservation.objects.filter(
            check_in_date__lte=current_date,
            check_out_date__gt=current_date,
            status='checked_in'
        ).count()
        
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        occupancy_data.append({
            'date': current_date,
            'occupied_rooms': occupied_rooms,
            'total_rooms': total_rooms,
            'occupancy_rate': round(occupancy_rate, 2)
        })
        
        current_date += timedelta(days=1)
    
    # Calculate averages
    avg_occupancy = sum(day['occupancy_rate'] for day in occupancy_data) / len(occupancy_data) if occupancy_data else 0
    
    context = {
        'occupancy_data': occupancy_data,
        'avg_occupancy': round(avg_occupancy, 2),
        'start_date': start_date,
        'end_date': end_date,
        'total_rooms': total_rooms,
    }
    
    return render(request, 'reports/occupancy_report.html', context)

@login_required
def revenue_report(request):
    """Generate revenue report"""
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate revenue data
    payments = Payment.objects.filter(
        payment_date__date__range=[start_date, end_date],
        status='completed'
    )
    
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    payment_count = payments.count()
    avg_payment = payments.aggregate(avg=Avg('amount'))['avg'] or 0
    
    # Daily revenue breakdown
    daily_revenue = []
    current_date = start_date
    
    while current_date <= end_date:
        day_payments = payments.filter(payment_date__date=current_date)
        day_revenue = day_payments.aggregate(total=Sum('amount'))['total'] or 0
        
        daily_revenue.append({
            'date': current_date,
            'revenue': day_revenue,
            'payment_count': day_payments.count()
        })
        
        current_date += timedelta(days=1)
    
    context = {
        'total_revenue': total_revenue,
        'payment_count': payment_count,
        'avg_payment': round(avg_payment, 2),
        'daily_revenue': daily_revenue,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'reports/revenue_report.html', context)

@login_required
def guest_history_report(request):
    """Generate guest history report"""
    guests = Guest.objects.annotate(
        reservation_count=Count('reservations'),
        total_spent=Sum('reservations__total_amount')
    ).order_by('-reservation_count')
    
    # Top guests
    top_guests = guests[:10]
    
    # Guest statistics
    total_guests = guests.count()
    repeat_guests = guests.filter(reservation_count__gt=1).count()
    vip_guests = guests.filter(is_vip=True).count()
    
    context = {
        'top_guests': top_guests,
        'total_guests': total_guests,
        'repeat_guests': repeat_guests,
        'vip_guests': vip_guests,
        'repeat_guest_percentage': round((repeat_guests / total_guests * 100) if total_guests > 0 else 0, 2),
    }
    
    return render(request, 'reports/guest_history_report.html', context)
