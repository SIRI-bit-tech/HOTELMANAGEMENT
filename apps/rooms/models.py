from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel


class RoomType(TimeStampedModel):
    """Room type/category definition"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy = models.PositiveIntegerField(default=2)
    size_sqft = models.PositiveIntegerField(null=True, blank=True)

    # Amenities
    has_wifi = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_minibar = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    has_kitchen = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(TimeStampedModel):
    """Individual room"""
    ROOM_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('cleaning', 'Being Cleaned'),
        ('out_of_order', 'Out of Order'),
    ]

    number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    floor = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='available')

    # Room-specific details
    notes = models.TextField(blank=True)
    last_maintenance = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['number']
        indexes = [
            models.Index(fields=['status', 'room_type']),
            models.Index(fields=['floor', 'number']),
        ]

    def __str__(self):
        return f"Room {self.number} ({self.room_type.name})"

    @property
    def is_available(self):
        return self.status == 'available'

    def get_current_reservation(self):
        """Get current active reservation for this room"""
        from apps.reservations.models import Reservation
        from django.utils import timezone

        return Reservation.objects.filter(
            room=self,
            check_in_date__lte=timezone.now().date(),
            check_out_date__gt=timezone.now().date(),
            status__in=['confirmed', 'checked_in']
        ).first()


class RoomImage(TimeStampedModel):
    """Room images"""
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.room_type.name} - Image {self.id}"


class RoomAmenity(TimeStampedModel):
    """Additional room amenities"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # CSS class or icon name
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Room Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name


class RoomTypeAmenity(models.Model):
    """Many-to-many relationship between room types and amenities"""
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    amenity = models.ForeignKey(RoomAmenity, on_delete=models.CASCADE)
    is_complimentary = models.BooleanField(default=True)
    additional_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        unique_together = ['room_type', 'amenity']

    def __str__(self):
        return f"{self.room_type.name} - {self.amenity.name}"
