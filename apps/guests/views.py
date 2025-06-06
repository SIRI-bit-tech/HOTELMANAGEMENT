from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Guest
from .forms import GuestForm


@login_required
def guest_list(request):
    """Display list of all guests with search and filtering"""
    guests = Guest.objects.all().order_by('-created_at')

    # Search functionality
    search = request.GET.get('search')
    if search:
        guests = guests.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(identification_number__icontains=search)
        )

    # Filter by VIP status
    is_vip = request.GET.get('is_vip')
    if is_vip:
        guests = guests.filter(is_vip=True)

    # Pagination
    paginator = Paginator(guests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'guests': page_obj,
        'search': search,
        'is_vip': is_vip,
    }

    if request.htmx:
        return render(request, 'guests/partials/guest_list_partial.html', context)

    return render(request, 'guests/guest_list.html', context)


@login_required
def guest_detail(request, guest_id):
    """Display guest details and reservation history"""
    guest = get_object_or_404(Guest, id=guest_id)

    # Get reservation history
    reservations = guest.reservations.all().order_by('-created_at')

    # Get current reservation
    current_reservation = guest.reservations.filter(
        status='checked_in'
    ).first()

    # Get upcoming reservations
    upcoming_reservations = guest.reservations.filter(
        status='confirmed',
        check_in_date__gte=timezone.now().date()
    ).order_by('check_in_date')

    context = {
        'guest': guest,
        'reservations': reservations,
        'current_reservation': current_reservation,
        'upcoming_reservations': upcoming_reservations,
    }

    return render(request, 'guests/guest_detail.html', context)


@login_required
def create_guest(request):
    """Create a new guest"""
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Guest {guest.full_name} created successfully!')
            return redirect('guests:guest_detail', guest_id=guest.id)
    else:
        form = GuestForm()

    context = {'form': form, 'title': 'Add New Guest'}
    return render(request, 'guests/guest_form.html', context)


@login_required
def edit_guest(request, guest_id):
    """Edit an existing guest"""
    guest = get_object_or_404(Guest, id=guest_id)

    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            guest = form.save()
            messages.success(request, f'Guest {guest.full_name} updated successfully!')
            return redirect('guests:guest_detail', guest_id=guest.id)
    else:
        form = GuestForm(instance=guest)

    context = {'form': form, 'guest': guest, 'title': 'Edit Guest'}
    return render(request, 'guests/guest_form.html', context)


@login_required
def guest_search(request):
    """HTMX endpoint for guest search"""
    query = request.GET.get('q', '')

    if len(query) >= 2:
        guests = Guest.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )[:10]
    else:
        guests = []

    context = {'guests': guests, 'query': query}
    return render(request, 'guests/partials/guest_search_results.html', context)
