"""Poslovna pravila tur: sestavljanje, kapaciteta vozila in napredek dostav"""

from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from users.models import User

from .models import Order, Stop, Tour, Vehicle

# Naročila, ki jih lahko disponent doda v turo
UNASSIGNED_STATUSES = [Order.Status.NEW, Order.Status.NOT_DELIVERED]


def tour_load(tour):
    """Vrne skupno težo in palete naročil v turi ter za koliko je kapaciteta vozila presežena"""
    orders = [stop.order for stop in tour.stops.all()]
    weight = sum((order.weight_kg for order in orders), Decimal(0))
    pallets = sum((order.pallets for order in orders), Decimal(0))
    # Vrednost, ki je točno enaka zmogljivosti, ni presežena
    weight_exceeded_by = max(weight - tour.vehicle.max_load_kg, Decimal(0))
    pallets_exceeded_by = max(pallets - tour.vehicle.pallet_spaces, Decimal(0))
    return {
        "total_weight_kg": weight,
        "total_pallets": pallets,
        "weight_exceeded_by": weight_exceeded_by,
        "pallets_exceeded_by": pallets_exceeded_by,
        "is_over_capacity": weight_exceeded_by > 0 or pallets_exceeded_by > 0,
    }


def delivery_progress(tour):
    """Vrne število vseh, dostavljenih in nedostavljenih postankov ture"""
    results = [stop.result for stop in tour.stops.all()]
    return {
        "stop_count": len(results),
        "delivered_count": results.count(Stop.Result.DELIVERED),
        "not_delivered_count": results.count(Stop.Result.NOT_DELIVERED),
    }


def available_vehicles(date):
    """Aktivna vozila, ki na ta datum še nimajo ture"""
    return Vehicle.objects.filter(is_active=True).exclude(tours__dispatch_date=date)


def available_drivers(date):
    """Aktivni vozniki, ki na ta datum še nimajo ture"""
    drivers = User.objects.filter(role=User.Role.DRIVER, is_active=True)
    return drivers.exclude(driven_tours__dispatch_date=date).order_by("first_name", "last_name")


def tour_creation_errors(date, vehicle, driver):
    """Vrne seznam razlogov, zakaj ture s tem vozilom in voznikom ni mogoče ustvariti"""
    errors = []
    if not available_vehicles(date).filter(pk=vehicle.pk).exists():
        errors.append("Vozilo ni aktivno ali ima na ta datum že turo")
    if not available_drivers(date).filter(pk=driver.pk).exists():
        errors.append("Voznik ni aktiven ali ima na ta datum že turo")
    return errors


def change_vehicle(tour, vehicle):
    """Zamenja vozilo osnutka, novo vozilo mora biti aktivno in na ta datum prosto"""
    if vehicle.pk == tour.vehicle_id:
        return
    errors = []
    if tour.status != Tour.Status.DRAFT:
        errors.append("Vozilo je mogoče zamenjati samo v osnutku ture")
    if not available_vehicles(tour.dispatch_date).filter(pk=vehicle.pk).exists():
        errors.append("Vozilo ni aktivno ali ima na ta datum že turo")
    if errors:
        raise ValidationError(errors)
    tour.vehicle = vehicle
    tour.save()


def unassigned_orders(date=None, region=None):
    """Nerazporejena naročila po roku odpreme, brez naročil, prejetih po datumu ture"""
    orders = Order.objects.filter(status__in=UNASSIGNED_STATUSES).select_related("customer")
    if date:
        orders = orders.filter(received_date__lte=date)
    if region:
        orders = orders.filter(customer__region=region)
    return orders.order_by("dispatch_deadline", "number")


@transaction.atomic
def add_stop(tour, order):
    """Doda naročilo na konec ture in ga označi kot planirano"""
    errors = []
    if order.status not in UNASSIGNED_STATUSES:
        errors.append("Naročilo je že v turi ali je dostavljeno")
    if order.received_date > tour.dispatch_date:
        errors.append("Naročilo je prejeto po datumu odpreme ture")
    if errors:
        raise ValidationError(errors)

    Stop.objects.create(tour=tour, order=order, sequence=tour.stops.count() + 1)
    order.status = Order.Status.PLANNED
    order.save()


@transaction.atomic
def remove_stop(stop):
    """Odstrani postanek, vrne naročilo med nerazporejena in preštevilči ostale postanke"""
    tour, order = stop.tour, stop.order
    stop.delete()
    order.status = Order.Status.NEW
    order.save()
    # Zaporedje ostane 1 … N brez lukenj
    for sequence, other in enumerate(tour.stops.order_by("sequence"), start=1):
        if other.sequence != sequence:
            other.sequence = sequence
            other.save()
