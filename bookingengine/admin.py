from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('apartman', 'customer', 'date_from', 'date_to', 'visitors_count', 'approved', 'created_at')
    list_filter = ('approved', 'apartman')
    search_fields = ('apartman__naziv', 'customer__name', 'customer__email') # Adjust customer fields as needed
    date_hierarchy = 'date_from'
    list_editable = ('approved',)
    raw_id_fields = ('apartman', 'customer')

    actions = ['approve_bookings']

    def approve_bookings(self, request, queryset):
        queryset.update(approved=True)
    approve_bookings.short_description = "Approve selected bookings"