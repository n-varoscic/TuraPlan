from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Order, Settings, Stop, Tour, Vehicle
from .services import (
    complete_errors, confirmation_errors, delivery_progress, split_customers, start_errors,
    tour_creation_errors, tour_load,
)


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "registration_number", "type", "max_load_kg", "pallet_spaces"]


class StopSerializer(serializers.ModelSerializer):
    """Postanek s podatki naročila in stranke, ki jih potrebujeta disponent in voznik"""

    order_number = serializers.CharField(source="order.number")
    customer_id = serializers.IntegerField(source="order.customer.id")
    customer = serializers.CharField(source="order.customer.name")
    delivery_note = serializers.CharField(source="order.customer.delivery_note")
    address = serializers.CharField(source="order.customer.address")
    city = serializers.CharField(source="order.customer.city")
    phone = serializers.CharField(source="order.customer.phone")
    # Koordinate stranke za zemljevid, None pomeni, da lokacija ni določena
    lat = serializers.FloatField(source="order.customer.lat")
    lng = serializers.FloatField(source="order.customer.lng")
    weight_kg = serializers.DecimalField(source="order.weight_kg", max_digits=8, decimal_places=2)
    pallets = serializers.DecimalField(source="order.pallets", max_digits=5, decimal_places=2)

    class Meta:
        model = Stop
        fields = [
            "id", "sequence", "order_number", "customer_id", "customer", "delivery_note", "address", "city",
            "phone", "lat", "lng", "weight_kg", "pallets", "driver_note", "result", "reason", "marked_at",
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

    def to_representation(self, tour):
        # Opozorila in razlogi, zakaj ture še ni mogoče potrditi, začeti ali zaključiti
        settings = Settings.load()
        return {
            **super().to_representation(tour),
            # Skladišče je začetna točka ture na zemljevidu
            "warehouse": {
                "address": settings.warehouse_address,
                "lat": settings.warehouse_lat,
                "lng": settings.warehouse_lng,
            },
            "split_customers": split_customers(tour),
            "confirmation_errors": confirmation_errors(tour),
            "start_errors": start_errors(tour),
            "complete_errors": complete_errors(tour),
        }


class TourCreateSerializer(serializers.ModelSerializer):
    """Nova tura z datumom odpreme, vozilom in voznikom"""

    class Meta:
        model = Tour
        fields = ["dispatch_date", "vehicle", "driver"]
        # Zasedenost vozila in voznika preverimo sami, da so razlogi v slovenščini
        validators = []

    def validate(self, data):
        errors = tour_creation_errors(data["dispatch_date"], data["vehicle"], data["driver"])
        if errors:
            raise serializers.ValidationError(errors)
        return data


class OrderSerializer(serializers.ModelSerializer):
    """Nerazporejeno naročilo z oznako, ali je datum ture po roku odpreme"""

    customer = serializers.CharField(source="customer.name")
    city = serializers.CharField(source="customer.city")
    region = serializers.CharField(source="customer.region")
    is_late = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "number", "customer", "city", "region", "received_date", "dispatch_deadline",
            "weight_kg", "pallets", "description", "status", "is_late",
        ]

    def get_is_late(self, order):
        date = self.context.get("date")
        return bool(date and date > order.dispatch_deadline)
