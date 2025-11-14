from django.urls import path
from .views import (
    TerminListView,
    TerminDetailView,
    TerminCreateView,
    TerminUpdateView,
    TerminDeleteView,
)

urlpatterns = [
    path('', TerminListView.as_view(), name='termin_list'),
    path('termin/<int:pk>/', TerminDetailView.as_view(), name='termin_detail'),
    path('termin/new/', TerminCreateView.as_view(), name='termin_create'),
    path('termin/<int:pk>/edit/', TerminUpdateView.as_view(), name='termin_update'),
    path('termin/<int:pk>/delete/', TerminDeleteView.as_view(), name='termin_delete'),
]