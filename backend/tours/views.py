from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsDispatcher
from users.serializers import UserSerializer

from .models import Order, Stop, Tour, Vehicle
from .serializers import (
    OrderSerializer, TourCreateSerializer, TourDetailSerializer, TourListSerializer, VehicleSerializer,
)
from .services import (
    add_stop, available_drivers, available_vehicles, change_vehicle, confirm_tour, move_stop, move_stop_to,
    remove_stop, unassigned_orders, unconfirm_tour, update_customer_delivery_note, update_driver_note,
)


def tours_with_details():
    """Ture z vozilom, voznikom in postanki, naloženimi z malo poizvedbami"""
    return Tour.objects.select_related("vehicle", "driver").prefetch_related("stops__order__customer")


def parse_date(value):
    """Datum iz parametra naslova, napačen datum vrne 400 z razlogom"""
    return serializers.DateField().to_internal_value(value)


def tour_response(tour, status_code=status.HTTP_200_OK):
    """Vrne celotno turo s postanki, da frontend takoj prikaže novo stanje"""
    return Response(TourDetailSerializer(tours_with_details().get(pk=tour.pk)).data, status=status_code)


class TourListView(generics.ListAPIView):
    """GET /api/tours/ s filtri ?date_from=, ?date_to= in ?status=, POST /api/tours/ ustvari turo"""

    permission_classes = [IsDispatcher]
    serializer_class = TourListSerializer

    def get_queryset(self):
        tours = tours_with_details()
        params = self.request.query_params
        if params.get("date_from"):
            tours = tours.filter(dispatch_date__gte=parse_date(params["date_from"]))
        if params.get("date_to"):
            tours = tours.filter(dispatch_date__lte=parse_date(params["date_to"]))
        if params.get("status"):
            tours = tours.filter(status=params["status"])
        return tours

    def post(self, request):
        serializer = TourCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tour = serializer.save(created_by=request.user)
        return tour_response(tour, status.HTTP_201_CREATED)


class TourDetailView(generics.RetrieveAPIView):
    """GET /api/tours/{id}/ s postanki, PATCH /api/tours/{id}/ zamenja vozilo"""

    permission_classes = [IsDispatcher]
    serializer_class = TourDetailSerializer
    queryset = tours_with_details()

    def patch(self, request, pk):
        tour = get_object_or_404(Tour, pk=pk)
        vehicle = get_object_or_404(Vehicle, pk=request.data.get("vehicle"))
        change_vehicle(tour, vehicle)
        return tour_response(tour)


class TourOptionsView(APIView):
    """GET /api/tours/options/?date= vrne prosta vozila in voznike za novo turo"""

    permission_classes = [IsDispatcher]

    def get(self, request):
        date = parse_date(request.query_params.get("date", ""))
        return Response({
            "vehicles": VehicleSerializer(available_vehicles(date), many=True).data,
            "drivers": UserSerializer(available_drivers(date), many=True).data,
        })


class OrderListView(generics.ListAPIView):
    """GET /api/orders/?date=&region= vrne nerazporejena naročila"""

    permission_classes = [IsDispatcher]
    serializer_class = OrderSerializer

    def get_date(self):
        value = self.request.query_params.get("date")
        return parse_date(value) if value else None

    def get_queryset(self):
        return unassigned_orders(self.get_date(), self.request.query_params.get("region"))

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "date": self.get_date()}


class TourStopsView(APIView):
    """POST /api/tours/{id}/stops/ doda naročilo v turo"""

    permission_classes = [IsDispatcher]

    def post(self, request, pk):
        tour = get_object_or_404(Tour, pk=pk)
        order = get_object_or_404(Order, pk=request.data.get("order"))
        add_stop(tour, order)
        return tour_response(tour, status.HTTP_201_CREATED)


class StopDetailView(APIView):
    """PATCH /api/stops/{id}/ shrani opombo za voznika, DELETE /api/stops/{id}/ odstrani postanek iz ture"""

    permission_classes = [IsDispatcher]

    def patch(self, request, pk):
        stop = get_object_or_404(Stop, pk=pk)
        update_driver_note(stop, request.data.get("driver_note", ""))
        return tour_response(stop.tour)

    def delete(self, request, pk):
        stop = get_object_or_404(Stop, pk=pk)
        remove_stop(stop)
        return tour_response(stop.tour)


class StopMoveView(APIView):
    """POST /api/stops/{id}/move/ z {"direction": "up" | "down"} ali {"position": 3} premakne postanek"""

    permission_classes = [IsDispatcher]

    def post(self, request, pk):
        stop = get_object_or_404(Stop, pk=pk)
        if "position" in request.data:
            position = serializers.IntegerField().to_internal_value(request.data["position"])
            move_stop_to(stop, position)
        else:
            move_stop(stop, request.data.get("direction"))
        return tour_response(stop.tour)


class StopDeliveryNoteView(APIView):
    """POST /api/stops/{id}/delivery-note/ shrani stalno opombo stranke tega postanka"""

    permission_classes = [IsDispatcher]

    def post(self, request, pk):
        stop = get_object_or_404(Stop, pk=pk)
        update_customer_delivery_note(stop, request.data.get("delivery_note", ""))
        return tour_response(stop.tour)


class TourConfirmView(APIView):
    """POST /api/tours/{id}/confirm/ potrdi turo, sicer vrne vse neizpolnjene pogoje"""

    permission_classes = [IsDispatcher]

    def post(self, request, pk):
        tour = get_object_or_404(tours_with_details(), pk=pk)
        confirm_tour(tour)
        return tour_response(tour)


class TourUnconfirmView(APIView):
    """POST /api/tours/{id}/unconfirm/ vrne potrjeno turo v osnutek"""

    permission_classes = [IsDispatcher]

    def post(self, request, pk):
        tour = get_object_or_404(Tour, pk=pk)
        unconfirm_tour(tour)
        return tour_response(tour)
