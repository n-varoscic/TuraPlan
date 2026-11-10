from rest_framework import generics, serializers

from users.permissions import IsDispatcher

from .models import Tour
from .serializers import TourDetailSerializer, TourListSerializer


def tours_with_details():
    """Ture z vozilom, voznikom in postanki, naloženimi z malo poizvedbami"""
    return Tour.objects.select_related("vehicle", "driver").prefetch_related("stops__order__customer")


class TourListView(generics.ListAPIView):
    """GET /api/tours/ s filtri ?date_from=, ?date_to= in ?status="""

    permission_classes = [IsDispatcher]
    serializer_class = TourListSerializer

    def get_queryset(self):
        tours = tours_with_details()
        params = self.request.query_params
        # Napačen datum vrne 400 z razlogom
        if params.get("date_from"):
            tours = tours.filter(dispatch_date__gte=serializers.DateField().to_internal_value(params["date_from"]))
        if params.get("date_to"):
            tours = tours.filter(dispatch_date__lte=serializers.DateField().to_internal_value(params["date_to"]))
        if params.get("status"):
            tours = tours.filter(status=params["status"])
        return tours


class TourDetailView(generics.RetrieveAPIView):
    """GET /api/tours/{id}/ s postanki"""

    permission_classes = [IsDispatcher]
    serializer_class = TourDetailSerializer
    queryset = tours_with_details()
