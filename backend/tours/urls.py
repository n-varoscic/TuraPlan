from django.urls import path

from .views import (
    OrderListView, StopDeliveryNoteView, StopDetailView, StopMoveView, TourConfirmView, TourDetailView,
    TourListView, TourOptionsView, TourStopsView, TourUnconfirmView,
)

urlpatterns = [
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/options/", TourOptionsView.as_view(), name="tour-options"),
    path("tours/<int:pk>/", TourDetailView.as_view(), name="tour-detail"),
    path("tours/<int:pk>/stops/", TourStopsView.as_view(), name="tour-stops"),
    path("tours/<int:pk>/confirm/", TourConfirmView.as_view(), name="tour-confirm"),
    path("tours/<int:pk>/unconfirm/", TourUnconfirmView.as_view(), name="tour-unconfirm"),
    path("stops/<int:pk>/", StopDetailView.as_view(), name="stop-detail"),
    path("stops/<int:pk>/move/", StopMoveView.as_view(), name="stop-move"),
    path("stops/<int:pk>/delivery-note/", StopDeliveryNoteView.as_view(), name="stop-delivery-note"),
    path("orders/", OrderListView.as_view(), name="order-list"),
]
