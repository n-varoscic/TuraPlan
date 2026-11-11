from django.urls import path

from .views import (
    MyTourListView, OrderListView, OrderSearchView, StopDeliveryNoteView, StopDetailView, StopMoveView,
    StopResultView, TourCompleteView, TourConfirmView, TourDetailView, TourListView,
    TourOptionsView, TourRouteView, TourStartView, TourStopsView, TourSuggestedOrderView,
    TourUnconfirmView,
)

urlpatterns = [
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/options/", TourOptionsView.as_view(), name="tour-options"),
    path("tours/<int:pk>/", TourDetailView.as_view(), name="tour-detail"),
    path("tours/<int:pk>/stops/", TourStopsView.as_view(), name="tour-stops"),
    path("tours/<int:pk>/suggested-order/", TourSuggestedOrderView.as_view(), name="tour-suggested-order"),
    path("tours/<int:pk>/route/", TourRouteView.as_view(), name="tour-route"),
    path("tours/<int:pk>/confirm/", TourConfirmView.as_view(), name="tour-confirm"),
    path("tours/<int:pk>/unconfirm/", TourUnconfirmView.as_view(), name="tour-unconfirm"),
    path("tours/<int:pk>/start/", TourStartView.as_view(), name="tour-start"),
    path("tours/<int:pk>/complete/", TourCompleteView.as_view(), name="tour-complete"),
    path("my-tours/", MyTourListView.as_view(), name="my-tours"),
    path("stops/<int:pk>/", StopDetailView.as_view(), name="stop-detail"),
    path("stops/<int:pk>/move/", StopMoveView.as_view(), name="stop-move"),
    path("stops/<int:pk>/result/", StopResultView.as_view(), name="stop-result"),
    path("stops/<int:pk>/delivery-note/", StopDeliveryNoteView.as_view(), name="stop-delivery-note"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/search/", OrderSearchView.as_view(), name="order-search"),
]
