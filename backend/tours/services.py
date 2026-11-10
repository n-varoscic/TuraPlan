"""Poslovna pravila tur: zasedenost vozila in napredek dostav"""

from decimal import Decimal

from .models import Stop


def tour_load(tour):
    """Vrne skupno težo in palete vseh naročil v turi"""
    orders = [stop.order for stop in tour.stops.all()]
    return {
        "total_weight_kg": sum((order.weight_kg for order in orders), Decimal(0)),
        "total_pallets": sum((order.pallets for order in orders), Decimal(0)),
    }


def delivery_progress(tour):
    """Vrne število vseh, dostavljenih in nedostavljenih postankov ture"""
    results = [stop.result for stop in tour.stops.all()]
    return {
        "stop_count": len(results),
        "delivered_count": results.count(Stop.Result.DELIVERED),
        "not_delivered_count": results.count(Stop.Result.NOT_DELIVERED),
    }
