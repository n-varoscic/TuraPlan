from django.urls import path

from .views import (
    OrderListView, StopDeliveryNoteView, StopDetailView, StopMoveView, TourDetailView, TourListView,
    TourOptionsView, TourStopsView,
)

urlpatterns = [
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/options/", TourOptionsView.as_view(), name="tour-options"),
    path("tours/<int:pk>/", TourDetailView.as_view(), name="tour-detail"),
    path("tours/<int:pk>/stops/", TourStopsView.as_view(), name="tour-stops"),
    path("stops/<int:pk>/", StopDetailView.as_view(), name="stop-detail"),
    path("stops/<int:pk>/move/", StopMoveView.as_view(), name="stop-move"),
    path("stops/<int:pk>/delivery-note/", StopDeliveryNoteView.as_view(), name="stop-delivery-note"),
    path("orders/", OrderListView.as_view(), name="order-list"),
]
