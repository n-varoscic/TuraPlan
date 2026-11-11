"""Poslovna pravila tur: sestavljanje, kapaciteta vozila, potrditev in izvedba dostav"""

import json
from decimal import Decimal
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from users.models import User

from .models import Order, Settings, Stop, Tour, Vehicle

# Naročila, ki jih lahko disponent doda v turo
UNASSIGNED_STATUSES = [Order.Status.NEW, Order.Status.NOT_DELIVERED]

# Opomba za voznika in stalna opomba stranke imata največ 300 znakov
DRIVER_NOTE_MAX_LENGTH = 300

# Brezplačna storitev OpenStreetMap, ki iz naslova vrne koordinate
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Polmer Zemlje za izračun zračne razdalje
EARTH_RADIUS_KM = 6371


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


def customer_address(customer):
    """Poln naslov stranke, po katerem iščemo koordinate"""
    return f"{customer.address}, {customer.postal_code} {customer.city}"


def geocode(address):
    """Vrne (lat, lng) naslova iz storitve Nominatim ali None, če lokacije ni mogoče določiti"""
    params = urlencode({"format": "json", "limit": 1, "countrycodes": "si", "q": address})
    # Storitev zahteva, da se aplikacija predstavi z glavo User-Agent
    headers = {"User-Agent": "TuraPlan/1.0 (studentski projekt)"}
    request = Request(f"{NOMINATIM_URL}?{params}", headers=headers)
    try:
        with urlopen(request, timeout=5) as response:
            results = json.load(response)
    except (OSError, ValueError):
        # Storitev ni dosegljiva ali je vrnila neveljaven odgovor
        return None
    if not results:
        return None
    return round(Decimal(results[0]["lat"]), 6), round(Decimal(results[0]["lon"]), 6)


def locate_customer(customer):
    """Poišče in shrani koordinate stranke, če jih še nima ali se je njen naslov spremenil"""
    address = customer_address(customer)
    if customer.lat is not None and customer.geocoded_address == address:
        return
    location = geocode(address)
    if location:
        customer.lat, customer.lng = location
        customer.geocoded_address = address
    else:
        # Stare koordinate za nov naslov ne veljajo, zato stranka ostane brez lokacije
        customer.lat = customer.lng = None
        customer.geocoded_address = ""
    customer.save()


@transaction.atomic
def add_stop(tour, order):
    """Doda naročilo na konec ture in ga označi kot planirano"""
    ensure_draft(tour)
    errors = []
    if order.status not in UNASSIGNED_STATUSES:
        errors.append("Naročilo je že v turi ali je dostavljeno")
    if order.received_date > tour.dispatch_date:
        errors.append("Naročilo je prejeto po datumu odpreme ture")
    if errors:
        raise ValidationError(errors)

    # Naročilo se doda tudi, če lokacije stranke ni mogoče določiti
    locate_customer(order.customer)

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
    ensure_draft(stop.tour)
    stops = list(stop.tour.stops.order_by("sequence"))
    if not 1 <= position <= len(stops):
        raise ValidationError([f"Mesto mora biti med 1 in {len(stops)}"])
    stops.remove(stop)
    stops.insert(position - 1, stop)
    renumber_stops(stop.tour, stops)


def renumber_stops(tour, stops):
    """Postankom ture shrani zaporedne številke 1 … N po vrstnem redu v seznamu stops"""
    # Najprej vsem postankom damo začasne številke nad obstoječimi,
    # ker ima vsaka številka v turi lahko samo en postanek
    tour.stops.update(sequence=F("sequence") + len(stops))
    for sequence, stop in enumerate(stops, start=1):
        stop.sequence = sequence
        stop.save()


def move_stop(stop, direction):
    """Premakne postanek za eno mesto gor (up) ali dol (down)"""
    ensure_draft(stop.tour)
    if direction not in ("up", "down"):
        raise ValidationError(["Smer mora biti up ali down"])
    position = stop.sequence - 1 if direction == "up" else stop.sequence + 1
    if position < 1:
        raise ValidationError(["Postanek je že na prvem mestu"])
    if position > stop.tour.stops.count():
        raise ValidationError(["Postanek je že na zadnjem mestu"])
    move_stop_to(stop, position)


def distance_km(start, end):
    """Zračna razdalja v km med točkama (lat, lng) po formuli haversine"""
    lat1, lng1, lat2, lng2 = (radians(float(value)) for value in (*start, *end))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))


def warehouse_location():
    """Koordinate skladišča (lat, lng), kjer se začne vsaka tura"""
    settings = Settings.load()
    return settings.warehouse_lat, settings.warehouse_lng


def route_distance_km(stops):
    """Skupna zračna razdalja od skladišča po postankih v danem vrstnem redu, na 0,1 km"""
    points = [warehouse_location()]
    points += [(stop.order.customer.lat, stop.order.customer.lng) for stop in stops]
    # Skladišča ali postanka brez lokacije pri razdalji ne upoštevamo
    points = [point for point in points if None not in point]
    return round(sum(distance_km(a, b) for a, b in zip(points, points[1:])), 1)


def suggested_order(tour):
    """Predlog vrstnega reda postankov: od skladišča vsakič najbližja še neobiskana stranka"""
    ensure_draft(tour)
    position = warehouse_location()
    if None in position:
        raise ValidationError(["Skladišče nima določene lokacije"])

    # Postanke iste stranke obravnavamo kot eno točko, zato v predlogu ostanejo zaporedni
    stops_by_customer = {}
    for stop in tour.stops.select_related("order__customer").order_by("sequence"):
        stops_by_customer.setdefault(stop.order.customer, []).append(stop)
    located = [customer for customer in stops_by_customer if customer.lat is not None]
    # Stranke brez koordinat gredo na konec v obstoječem vrstnem redu
    not_located = [customer for customer in stops_by_customer if customer.lat is None]

    ordered = []
    while located:
        nearest = min(located, key=lambda customer: distance_km(position, (customer.lat, customer.lng)))
        located.remove(nearest)
        ordered.append(nearest)
        position = (nearest.lat, nearest.lng)
    return [stop for customer in ordered + not_located for stop in stops_by_customer[customer]]


def suggested_order_preview(tour):
    """Predlagani vrstni red z razdaljo in trenutna razdalja za primerjavo, v bazo se nič ne shrani"""
    stops = suggested_order(tour)
    current_distance_km = route_distance_km(tour.stops.select_related("order__customer").order_by("sequence"))
    # Številke predloga nastavimo samo v pomnilniku, da jih prikažeta seznam in zemljevid
    for sequence, stop in enumerate(stops, start=1):
        stop.sequence = sequence
    return {
        "stops": stops,
        "distance_km": route_distance_km(stops),
        "current_distance_km": current_distance_km,
    }


@transaction.atomic
def apply_suggested_order(tour):
    """Shrani predlagani vrstni red; disponent lahko postanke potem še ročno premika"""
    renumber_stops(tour, suggested_order(tour))


def pluralize(count, forms):
    """Število z ustreznim sklonom, forms so oblike za 1, 2, 3 in 4 ter 5 ali več: 2 znaka, 5 znakov"""
    one, two, few, many = forms
    words = {1: one, 2: two, 3: few, 4: few}
    return f"{format_number(count)} {words.get(count % 100, many)}"


def characters(count):
    """Število znakov s pravilnim sklonom: 1 znak, 2 znaka, 3 znake, 5 znakov"""
    return pluralize(count, ["znak", "znaka", "znake", "znakov"])


def format_number(value):
    """Število v slovenski obliki: 1.200, 1,5"""
    text = f"{Decimal(value):,.2f}".rstrip("0").rstrip(".")
    return text.translate(str.maketrans({",": ".", ".": ","}))


def format_pallets(value):
    """Palete v tožilniku za »presežena za …«: 1 paleto, 2 paleti, 1,5 palete, 5 palet"""
    if Decimal(value) != Decimal(value).to_integral_value():
        return f"{format_number(value)} palete"
    return pluralize(int(value), ["paleto", "paleti", "palete", "palet"])


def ensure_draft(tour):
    """Potrjene ture in ture v dostavi so zaklenjene za urejanje"""
    if tour.status != Tour.Status.DRAFT:
        raise ValidationError(["Turo je mogoče spreminjati samo v osnutku"])


def confirmation_errors(tour):
    """Vsi razlogi, zakaj ture še ni mogoče potrditi"""
    errors = []
    if tour.status != Tour.Status.DRAFT:
        errors.append("Potrditi je mogoče samo turo v osnutku")
    if not tour.vehicle_id:
        errors.append("Tura nima vozila")
    if not tour.driver_id:
        errors.append("Tura nima voznika")
    if not tour.stops.exists():
        errors.append("Tura nima nobenega postanka")
    load = tour_load(tour)
    if load["weight_exceeded_by"] > 0:
        errors.append(f"Kapaciteta je presežena za {format_number(load['weight_exceeded_by'])} kg")
    if load["pallets_exceeded_by"] > 0:
        errors.append(f"Kapaciteta je presežena za {format_pallets(load['pallets_exceeded_by'])}")
    return errors


def confirm_tour(tour):
    """Potrdi turo in zabeleži čas potrditve; potrjeno turo vidi voznik"""
    errors = confirmation_errors(tour)
    if errors:
        raise ValidationError(errors)
    tour.status = Tour.Status.CONFIRMED
    tour.confirmed_at = timezone.now()
    tour.save()


def unconfirm_tour(tour):
    """Vrne potrjeno turo v osnutek, dokler je voznik ni začel"""
    if tour.status in (Tour.Status.IN_DELIVERY, Tour.Status.COMPLETED):
        raise ValidationError(["Voznik je turo že začel, zato je ni mogoče vrniti v osnutek"])
    if tour.status != Tour.Status.CONFIRMED:
        raise ValidationError(["Tura ni potrjena"])
    tour.status = Tour.Status.DRAFT
    tour.confirmed_at = None
    tour.save()


def update_driver_note(stop, note):
    """Shrani opombo za voznika, ki ima lahko največ 300 znakov"""
    ensure_draft(stop.tour)
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
    ensure_draft(stop.tour)
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
    ensure_draft(stop.tour)
    tour, order = stop.tour, stop.order
    stop.delete()
    order.status = Order.Status.NEW
    order.save()
    # Zaporedje ostane 1 … N brez lukenj
    for sequence, other in enumerate(tour.stops.order_by("sequence"), start=1):
        if other.sequence != sequence:
            other.sequence = sequence
            other.save()


# Ture, ki jih voznik vidi: osnutki so samo za disponenta
DRIVER_VISIBLE_STATUSES = [Tour.Status.CONFIRMED, Tour.Status.IN_DELIVERY, Tour.Status.COMPLETED]


def driver_tours(driver):
    """Potrjene, začete in zaključene ture voznika"""
    return Tour.objects.filter(driver=driver, status__in=DRIVER_VISIBLE_STATUSES)


def start_errors(tour):
    """Vsi razlogi, zakaj voznik ture še ne more začeti"""
    errors = []
    if tour.status != Tour.Status.CONFIRMED:
        errors.append("Začeti je mogoče samo potrjeno turo")
    if timezone.localdate() < tour.dispatch_date:
        errors.append("Turo je mogoče začeti najprej na datum odpreme")
    started = Tour.objects.filter(driver=tour.driver, status=Tour.Status.IN_DELIVERY).exclude(pk=tour.pk)
    if started.exists():
        errors.append("Najprej zaključi turo, ki je že v dostavi")
    return errors


def start_tour(tour):
    """Voznik začne turo, tura je v dostavi"""
    errors = start_errors(tour)
    if errors:
        raise ValidationError(errors)
    tour.status = Tour.Status.IN_DELIVERY
    tour.started_at = timezone.now()
    tour.save()


@transaction.atomic
def mark_stop(stop, result, reason=""):
    """Označi dostavo ali nedostavo; dokler je tura v dostavi, lahko voznik oznako popravi"""
    tour, order = stop.tour, stop.order
    reason = reason.strip()
    errors = []
    if tour.status != Tour.Status.IN_DELIVERY:
        errors.append("Postanke je mogoče označiti samo v turi, ki je v dostavi")
    # Nedostavljeno naročilo je disponent morda že dodal v novo turo, zato oznake ne smemo več spremeniti
    if stop.result == Stop.Result.NOT_DELIVERED and order.status != Order.Status.NOT_DELIVERED:
        errors.append("Naročilo je že v novi turi, zato oznake ni mogoče spremeniti")
    if result not in (Stop.Result.DELIVERED, Stop.Result.NOT_DELIVERED):
        errors.append("Rezultat mora biti DELIVERED ali NOT_DELIVERED")
    if result == Stop.Result.NOT_DELIVERED and not reason:
        errors.append("Razlog nedostave je obvezen")
    if errors:
        raise ValidationError(errors)

    stop.result = result
    stop.reason = reason if result == Stop.Result.NOT_DELIVERED else ""
    stop.marked_at = timezone.now()
    stop.save()
    # Nedostavljeno naročilo se vrne med nerazporejena za ponovno planiranje
    order.status = Order.Status.DELIVERED if result == Stop.Result.DELIVERED else Order.Status.NOT_DELIVERED
    order.save()


def complete_errors(tour):
    """Vsi razlogi, zakaj voznik ture še ne more zaključiti"""
    errors = []
    if tour.status != Tour.Status.IN_DELIVERY:
        errors.append("Zaključiti je mogoče samo turo, ki je v dostavi")
    pending = tour.stops.filter(result=Stop.Result.PENDING).count()
    if pending:
        errors.append(f"Neoznačeni postanki: {pending}")
    return errors


def complete_tour(tour):
    """Voznik zaključi turo, ko so označeni vsi postanki; nato oznak ni več mogoče spreminjati"""
    errors = complete_errors(tour)
    if errors:
        raise ValidationError(errors)
    tour.status = Tour.Status.COMPLETED
    tour.completed_at = timezone.now()
    tour.save()
