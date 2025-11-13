from django.urls import path
from .views import (
    BookingListView,
    BookingDetailView,
    BookingCreateView,
    BookingUpdateView,
    BookingDeleteView,
)

urlpatterns = [
    path('', BookingListView.as_view(), name='booking_list'),
    path('booking/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('booking/new/', BookingCreateView.as_view(), name='booking_create'),
    path('booking/<int:pk>/edit/', BookingUpdateView.as_view(), name='booking_update'),
    path('booking/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),
]