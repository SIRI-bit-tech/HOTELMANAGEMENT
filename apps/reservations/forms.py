from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Reservation
from apps.guests.models import Guest
from apps.rooms.models import Room

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'guest', 'room', 'check_in_date', 'check_out_date', 
            'adults', 'children', 'total_amount', 'special_requests', 'notes'
        ]
        widgets = {
            'guest': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'room': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'check_in_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'check_out_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
            }),
            'adults': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'min': 1
            }),
            'children': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'min': 0
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'step': '0.01'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 3
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 3
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        room = cleaned_data.get('room')

        if check_in_date and check_out_date:
            if check_in_date >= check_out_date:
                raise ValidationError('Check-out date must be after check-in date.')
            
            if check_in_date < timezone.now().date():
                raise ValidationError('Check-in date cannot be in the past.')

        # Check room availability
        if room and check_in_date and check_out_date:
            conflicting_reservations = Reservation.objects.filter(
                room=room,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date,
                status__in=['confirmed', 'checked_in']
            )
            
            if self.instance.pk:
                conflicting_reservations = conflicting_reservations.exclude(pk=self.instance.pk)
            
            if conflicting_reservations.exists():
                raise ValidationError('Room is not available for the selected dates.')

        return cleaned_data

class CheckInForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 3,
                'placeholder': 'Check-in notes...'
            }),
        }

class CheckOutForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500',
                'rows': 3,
                'placeholder': 'Check-out notes...'
            }),
        }
