from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Stop, Tour, Vehicle
from .services import delivery_progress, tour_load


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "registration_number", "type", "max_load_kg", "pallet_spaces"]


class StopSerializer(serializers.ModelSerializer):
    """Postanek s podatki naročila in stranke, ki jih potrebujeta disponent in voznik"""

    order_number = serializers.CharField(source="order.number")
    customer = serializers.CharField(source="order.customer.name")
    address = serializers.CharField(source="order.customer.address")
    city = serializers.CharField(source="order.customer.city")
    weight_kg = serializers.DecimalField(source="order.weight_kg", max_digits=8, decimal_places=2)
    pallets = serializers.DecimalField(source="order.pallets", max_digits=5, decimal_places=2)

    class Meta:
        model = Stop
        fields = [
            "id", "sequence", "order_number", "customer", "address", "city", "weight_kg", "pallets",
            "driver_note", "result", "reason", "marked_at",
        ]


class TourListSerializer(serializers.ModelSerializer):
    """Tura za seznam: vozilo, voznik, zasedenost in napredek dostav"""

    vehicle = VehicleSerializer()
    driver = UserSerializer()

    class Meta:
        model = Tour
        fields = ["id", "dispatch_date", "status", "vehicle", "driver"]

    def to_representation(self, tour):
        # Izračunane vrednosti dodamo k podatkom iz baze
        data = super().to_representation(tour)
        return {**data, **tour_load(tour), **delivery_progress(tour)}


class TourDetailSerializer(TourListSerializer):
    """Tura s postanki in časi prehodov statusov"""

    stops = StopSerializer(many=True)

    class Meta(TourListSerializer.Meta):
        fields = TourListSerializer.Meta.fields + [
            "note", "confirmed_at", "started_at", "completed_at", "stops",
        ]
