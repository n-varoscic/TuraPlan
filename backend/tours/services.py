"""Poslovna pravila tur: sestavljanje, kapaciteta vozila in napredek dostav"""

from decimal import Decimal

from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from users.models import User

from .models import Order, Stop, Tour, Vehicle

# Naročila, ki jih lahko disponent doda v turo
UNASSIGNED_STATUSES = [Order.Status.NEW, Order.Status.NOT_DELIVERED]

# Opomba za voznika in stalna opomba stranke imata največ 300 znakov
DRIVER_NOTE_MAX_LENGTH = 300


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

    # Naročilo stranke, ki je že v turi, gre takoj za njen zadnji postanek, sicer na konec
    customer_stops = tour.stops.filter(order__customer=order.customer)
    if customer_stops.exists():
        sequence = customer_stops.order_by("-sequence").first().sequence + 1
        # Postanke za njim premaknemo za eno mesto naprej, od zadnjega proti prvemu,
        # da se zaporedni številki v isti turi nikoli ne podvojita
        for other in tour.stops.filter(sequence__gte=sequence).order_by("-sequence"):
            other.sequence += 1
            other.save()
    else:
        sequence = tour.stops.count() + 1

    Stop.objects.create(tour=tour, order=order, sequence=sequence)
    order.status = Order.Status.PLANNED
    order.save()


@transaction.atomic
def move_stop_to(stop, position):
    """Premakne postanek na mesto position, ostali postanki se zamaknejo"""
    stops = list(stop.tour.stops.order_by("sequence"))
    if not 1 <= position <= len(stops):
        raise ValidationError([f"Mesto mora biti med 1 in {len(stops)}"])
    stops.remove(stop)
    stops.insert(position - 1, stop)

    # Najprej vsem postankom damo začasne številke nad obstoječimi,
    # ker ima vsaka številka v turi lahko samo en postanek
    stop.tour.stops.update(sequence=F("sequence") + len(stops))
    for sequence, other in enumerate(stops, start=1):
        other.sequence = sequence
        other.save()


def move_stop(stop, direction):
    """Premakne postanek za eno mesto gor (up) ali dol (down)"""
    if direction not in ("up", "down"):
        raise ValidationError(["Smer mora biti up ali down"])
    position = stop.sequence - 1 if direction == "up" else stop.sequence + 1
    if position < 1:
        raise ValidationError(["Postanek je že na prvem mestu"])
    if position > stop.tour.stops.count():
        raise ValidationError(["Postanek je že na zadnjem mestu"])
    move_stop_to(stop, position)


def characters(count):
    """Število znakov s pravilnim sklonom: 1 znak, 2 znaka, 3 znake, 5 znakov"""
    words = {1: "znak", 2: "znaka", 3: "znake", 4: "znake"}
    return f"{count} {words.get(count % 100, 'znakov')}"


def update_driver_note(stop, note):
    """Shrani opombo za voznika, ki ima lahko največ 300 znakov"""
    note = note.strip()
    check_note_length(note)
    stop.driver_note = note
    stop.save()


def check_note_length(note):
    """Opomba ima lahko največ 300 znakov, sicer vrne, za koliko je predolga"""
    if len(note) > DRIVER_NOTE_MAX_LENGTH:
        raise ValidationError([f"Opomba je predolga za {characters(len(note) - DRIVER_NOTE_MAX_LENGTH)}"])


def update_customer_delivery_note(stop, note):
    """Shrani stalno opombo stranke postanka; enaka opomba za voznika ni več potrebna"""
    note = note.strip()
    check_note_length(note)
    customer = stop.order.customer
    customer.delivery_note = note
    customer.save()
    if note and stop.driver_note == note:
        stop.driver_note = ""
        stop.save()


def split_customers(tour):
    """Imena strank, katerih postanki v turi niso zaporedni"""
    customers = [stop.order.customer for stop in tour.stops.all()]
    # Stranka je razdeljena, če se pojavi v več ločenih skupinah zaporednih postankov
    groups = [
        customer for index, customer in enumerate(customers) if index == 0 or customers[index - 1] != customer
    ]
    return sorted({customer.name for customer in groups if groups.count(customer) > 1})


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
