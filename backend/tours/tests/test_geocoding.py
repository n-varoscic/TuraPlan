from decimal import Decimal
from urllib.error import URLError

import pytest

from tours import services
from tours.models import Order

LOCATION = (Decimal("46.050000"), Decimal("14.500000"))


@pytest.fixture
def geocode_calls(monkeypatch):
    """Zamenja Nominatim s funkcijo, ki vrne znane koordinate in si zapomni iskane naslove"""
    calls = []

    def fake_geocode(address):
        calls.append(address)
        return LOCATION

    monkeypatch.setattr("tours.services.geocode", fake_geocode)
    return calls


def add(client, tour, number):
    return client.post(f"/api/tours/{tour.id}/stops/", {"order": Order.objects.get(number=number).id})


def customer_without_location(number):
    customer = Order.objects.get(number=number).customer
    customer.lat = customer.lng = None
    customer.geocoded_address = ""
    customer.save()
    return customer


def test_adding_order_saves_customer_coordinates(dispatcher_client, draft_tour, geocode_calls):
    customer = customer_without_location("N-014")
    response = add(dispatcher_client, draft_tour, "N-014")
    customer.refresh_from_db()
    assert geocode_calls == ["Ormoška cesta 30, 2250 Ptuj"]
    assert (customer.lat, customer.lng) == LOCATION
    assert (response.data["stops"][0]["lat"], response.data["stops"][0]["lng"]) == (46.05, 14.5)


def test_coordinates_are_not_searched_again_for_same_customer(dispatcher_client, draft_tour, geocode_calls):
    # N-014 in N-024 sta naročili iste stranke
    customer_without_location("N-014")
    add(dispatcher_client, draft_tour, "N-014")
    add(dispatcher_client, draft_tour, "N-024")
    assert len(geocode_calls) == 1


def test_changed_address_is_located_again(dispatcher_client, draft_tour, geocode_calls):
    customer = Order.objects.get(number="N-014").customer
    customer.address = "Slovenski trg 3"
    customer.save()
    add(dispatcher_client, draft_tour, "N-014")
    customer.refresh_from_db()
    assert geocode_calls == ["Slovenski trg 3, 2250 Ptuj"]
    assert (customer.lat, customer.lng) == LOCATION


def test_order_is_added_when_location_cannot_be_found(dispatcher_client, draft_tour):
    # Fikstura no_nominatim vrne None, kot da storitev ni dosegljiva
    customer_without_location("N-014")
    response = add(dispatcher_client, draft_tour, "N-014")
    assert response.status_code == 201
    assert response.data["stops"][0]["lat"] is None


def test_unreachable_service_returns_no_location(monkeypatch):
    def unreachable(request, timeout):
        raise URLError("ni povezave")

    # Pravo funkcijo geocode vrnemo nazaj in zamenjamo samo klic v omrežje
    monkeypatch.undo()
    monkeypatch.setattr("tours.services.urlopen", unreachable)
    assert services.geocode("Glavni trg 5, 2000 Maribor") is None


def test_tour_detail_contains_warehouse_location(dispatcher_client, draft_tour):
    warehouse = dispatcher_client.get(f"/api/tours/{draft_tour.id}/").data["warehouse"]
    assert warehouse["address"] == "Tržaška cesta 65, 2000 Maribor"
    assert (float(warehouse["lat"]), float(warehouse["lng"])) == (46.523286, 15.650472)
