from django.contrib import admin
from django.utils.html import format_html
from .models import RoomType, Room, RoomImage, RoomAmenity, RoomTypeAmenity


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']


class RoomTypeAmenityInline(admin.TabularInline):
    model = RoomTypeAmenity
    extra = 1


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'max_occupancy', 'size_sqft', 'is_active', 'room_count']
    list_filter = ['is_active', 'max_occupancy', 'has_wifi', 'has_tv', 'has_ac']
    search_fields = ['name', 'description']
    inlines = [RoomImageInline, RoomTypeAmenityInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'base_price', 'max_occupancy', 'size_sqft')
        }),
        ('Amenities', {
            'fields': ('has_wifi', 'has_tv', 'has_ac', 'has_minibar', 'has_balcony', 'has_kitchen')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def room_count(self, obj):
        return obj.rooms.count()
    room_count.short_description = 'Number of Rooms'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'room_type', 'floor', 'status', 'is_active', 'last_maintenance']
    list_filter = ['room_type', 'floor', 'status', 'is_active']
    search_fields = ['number', 'room_type__name']
    list_editable = ['status']
    ordering = ['number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'room_type', 'floor')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room_type')


@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room_type', 'caption', 'is_primary', 'order']
    list_filter = ['room_type', 'is_primary']
    list_editable = ['is_primary', 'order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room_type')
