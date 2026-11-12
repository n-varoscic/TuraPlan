from decimal import Decimal

import pytest

from tours.models import Order, Settings, Tour
from tours.services import distance_km


def add(client, tour, number):
    return client.post(f"/api/tours/{tour.id}/stops/", {"order": Order.objects.get(number=number).id})


def place(number, lat, lng):
    """Stranki naročila nastavi znane koordinate, da je pričakovani vrstni red jasen"""
    customer = Order.objects.get(number=number).customer
    customer.lat = None if lat is None else Decimal(lat)
    customer.lng = None if lng is None else Decimal(lng)
    customer.save()


def numbers(stops):
    return [stop["order_number"] for stop in stops]


@pytest.fixture
def line_tour(dispatcher_client, draft_tour):
    """Osnutek s skladiščem na 46,0 in strankami proti severu, dodanimi v napačnem vrstnem redu"""
    settings = Settings.load()
    settings.warehouse_lat, settings.warehouse_lng = Decimal("46.0"), Decimal("15.0")
    settings.save()
    # N-014 in N-024 sta naročili iste stranke (Pekarna Klas)
    place("N-016", "46.3", "15.0")
    place("N-014", "46.1", "15.0")
    place("N-015", "46.2", "15.0")
    for number in ["N-016", "N-014", "N-015", "N-024"]:
        add(dispatcher_client, draft_tour, number)
    return draft_tour


def suggestion(client, tour):
    return client.get(f"/api/tours/{tour.id}/suggested-order/")


def accept(client, tour, stop_ids):
    return client.post(f"/api/tours/{tour.id}/suggested-order/", {"stop_ids": stop_ids}, format="json")


def test_distance_between_points_is_air_distance():
    # Ena stopinja zemljepisne širine je približno 111 km
    assert distance_km((46, 15), (47, 15)) == pytest.approx(111.2, abs=0.1)


def test_suggestion_starts_at_warehouse_and_takes_nearest_stop(dispatcher_client, line_tour):
    response = suggestion(dispatcher_client, line_tour)
    assert response.status_code == 200
    assert numbers(response.data["stops"]) == ["N-014", "N-024", "N-015", "N-016"]
    assert [stop["sequence"] for stop in response.data["stops"]] == [1, 2, 3, 4]


def test_suggestion_shows_suggested_and_current_distance(dispatcher_client, line_tour):
    data = suggestion(dispatcher_client, line_tour).data
    # Predlog gre naravnost proti severu (0,3 stopinje), trenutni vrstni red se vrača nazaj
    assert data["distance_km"] == pytest.approx(33.4, abs=0.1)
    assert data["current_distance_km"] == pytest.approx(66.7, abs=0.1)
    assert dispatcher_client.get(f"/api/tours/{line_tour.id}/").data["distance_km"] == data["current_distance_km"]


def test_suggestion_is_not_saved_until_accepted(dispatcher_client, line_tour):
    suggestion(dispatcher_client, line_tour)
    stops = dispatcher_client.get(f"/api/tours/{line_tour.id}/").data["stops"]
    # Vmes N-024 stoji takoj za N-014, ker naročili iste stranke ob dodajanju ostaneta skupaj
    assert numbers(stops) == ["N-016", "N-014", "N-024", "N-015"]


def test_accepted_suggestion_is_saved_and_stops_can_still_be_moved(dispatcher_client, line_tour):
    stop_ids = [stop["id"] for stop in suggestion(dispatcher_client, line_tour).data["stops"]]
    response = accept(dispatcher_client, line_tour, stop_ids)
    assert response.status_code == 200
    assert numbers(response.data["stops"]) == ["N-014", "N-024", "N-015", "N-016"]
    last = response.data["stops"][3]["id"]
    response = dispatcher_client.post(f"/api/stops/{last}/move/", {"position": 1})
    assert numbers(response.data["stops"]) == ["N-016", "N-014", "N-024", "N-015"]


def test_stops_of_same_customer_stay_together(dispatcher_client, line_tour):
    # Naročili iste stranke razdelimo, predlog ju spet postavi skupaj
    stop = line_tour.stops.get(order__number="N-024")
    dispatcher_client.post(f"/api/stops/{stop.id}/move/", {"position": 4})
    stops = numbers(suggestion(dispatcher_client, line_tour).data["stops"])
    assert stops.index("N-024") == stops.index("N-014") + 1


def test_stops_without_coordinates_go_to_end_in_existing_order(dispatcher_client, line_tour):
    place("N-016", None, None)
    place("N-019", None, None)
    add(dispatcher_client, line_tour, "N-019")
    stops = numbers(suggestion(dispatcher_client, line_tour).data["stops"])
    assert stops == ["N-014", "N-024", "N-015", "N-016", "N-019"]


def test_suggestion_is_only_for_draft_tour(dispatcher_client, tomorrow):
    confirmed = Tour.objects.get(dispatch_date=tomorrow, status=Tour.Status.CONFIRMED)
    for response in [
        suggestion(dispatcher_client, confirmed),
        accept(dispatcher_client, confirmed, []),
    ]:
        assert response.status_code == 400
        assert response.data == ["Turo je mogoče spreminjati samo v osnutku"]


def test_driver_cannot_request_suggestion(driver_client):
    tour = Tour.objects.filter(status=Tour.Status.DRAFT).first()
    assert suggestion(driver_client, tour).status_code == 403
