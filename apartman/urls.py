from django.urls import path
from .views import (
    ApartmanListView,
    ApartmanDetailView,
    ApartmanCreateView,
    ApartmanUpdateView,
    ApartmanDeleteView,
)

urlpatterns = [
    path('', ApartmanListView.as_view(), name='apartman_list'),
    path('apartman/<int:pk>/', ApartmanDetailView.as_view(), name='apartman_detail'),
    path('apartman/new/', ApartmanCreateView.as_view(), name='apartman_create'),
    path('apartman/<int:pk>/edit/', ApartmanUpdateView.as_view(), name='apartman_update'),
    path('apartman/<int:pk>/delete/', ApartmanDeleteView.as_view(), name='apartman_delete'),
]