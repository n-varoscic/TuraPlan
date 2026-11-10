from datetime import timedelta

import pytest
from django.utils import timezone

from tours.models import Order, Stop, Tour, Vehicle
from users.models import User


@pytest.fixture
def tomorrow():
    return timezone.localdate() + timedelta(days=1)


@pytest.fixture
def draft_tour(dispatcher_client, tomorrow):
    # Nova tura z vozilom in voznikom, ki jutri še nimata ture
    response = dispatcher_client.post("/api/tours/", {
        "dispatch_date": tomorrow,
        "vehicle": Vehicle.objects.get(registration_number="MB CD-456").id,
        "driver": User.objects.get(email="voznik2@turaplan.si").id,
    })
    assert response.status_code == 201
    return Tour.objects.get(pk=response.data["id"])


def order(number):
    return Order.objects.get(number=number)


def test_new_tour_is_draft_and_created_by_dispatcher(draft_tour):
    assert draft_tour.status == Tour.Status.DRAFT
    assert draft_tour.created_by.email == "disponent@turaplan.si"


def test_options_show_only_free_vehicles_and_drivers(dispatcher_client, tomorrow):
    data = dispatcher_client.get(f"/api/tours/options/?date={tomorrow}").data
    assert [v["registration_number"] for v in data["vehicles"]] == ["MB CD-456"]
    assert [d["email"] for d in data["drivers"]] == ["voznik2@turaplan.si"]


def test_tour_cannot_use_vehicle_that_already_has_tour(dispatcher_client, tomorrow):
    response = dispatcher_client.post("/api/tours/", {
        "dispatch_date": tomorrow,
        "vehicle": Vehicle.objects.get(registration_number="MB TR-789").id,
        "driver": User.objects.get(email="voznik2@turaplan.si").id,
    })
    assert response.status_code == 400
    assert "Vozilo ni aktivno ali ima na ta datum že turo" in response.data["non_field_errors"]


def test_tour_cannot_use_inactive_vehicle(dispatcher_client, tomorrow):
    vehicle = Vehicle.objects.get(registration_number="MB CD-456")
    vehicle.is_active = False
    vehicle.save()
    response = dispatcher_client.post("/api/tours/", {
        "dispatch_date": tomorrow, "vehicle": vehicle.id,
        "driver": User.objects.get(email="voznik2@turaplan.si").id,
    })
    assert response.status_code == 400


def test_unassigned_orders_are_new_or_not_delivered_sorted_by_deadline(dispatcher_client, tomorrow):
    orders = dispatcher_client.get(f"/api/orders/?date={tomorrow}").data
    assert {o["status"] for o in orders} == {"NEW", "NOT_DELIVERED"}
    deadlines = [o["dispatch_deadline"] for o in orders]
    assert deadlines == sorted(deadlines)


def test_unassigned_orders_can_be_filtered_by_region(dispatcher_client, tomorrow):
    orders = dispatcher_client.get(f"/api/orders/?date={tomorrow}&region=Gorenjska").data
    assert {o["region"] for o in orders} == {"Gorenjska"}


def test_orders_received_after_tour_date_are_hidden(dispatcher_client):
    yesterday = timezone.localdate() - timedelta(days=1)
    numbers = [o["number"] for o in dispatcher_client.get(f"/api/orders/?date={yesterday}").data]
    assert "N-013" in numbers
    assert "N-025" not in numbers


def test_order_after_deadline_is_marked_late(dispatcher_client, tomorrow):
    orders = {o["number"]: o for o in dispatcher_client.get(f"/api/orders/?date={tomorrow}").data}
    assert orders["N-013"]["is_late"] is True
    assert orders["N-025"]["is_late"] is False


def test_added_order_becomes_planned_and_gets_next_sequence(dispatcher_client, draft_tour):
    dispatcher_client.post(f"/api/tours/{draft_tour.id}/stops/", {"order": order("N-014").id})
    response = dispatcher_client.post(f"/api/tours/{draft_tour.id}/stops/", {"order": order("N-015").id})
    assert response.status_code == 201
    assert [s["sequence"] for s in response.data["stops"]] == [1, 2]
    assert order("N-015").status == Order.Status.PLANNED


def test_planned_order_cannot_be_added_again(dispatcher_client, draft_tour):
    response = dispatcher_client.post(f"/api/tours/{draft_tour.id}/stops/", {"order": order("N-011").id})
    assert response.status_code == 400


def test_order_received_after_tour_date_cannot_be_added(dispatcher_client, seeded):
    tour = Tour.objects.get(dispatch_date=timezone.localdate())
    tour.dispatch_date -= timedelta(days=1)
    tour.save()
    response = dispatcher_client.post(f"/api/tours/{tour.id}/stops/", {"order": order("N-025").id})
    assert response.status_code == 400
    assert "Naročilo je prejeto po datumu odpreme ture" in response.data


def test_removed_order_returns_to_new_and_sequences_close_gap(dispatcher_client, draft_tour):
    for number in ["N-014", "N-015", "N-016"]:
        dispatcher_client.post(f"/api/tours/{draft_tour.id}/stops/", {"order": order(number).id})
    first = Stop.objects.get(tour=draft_tour, sequence=1)
    response = dispatcher_client.delete(f"/api/stops/{first.id}/")
    assert response.status_code == 200
    assert [s["sequence"] for s in response.data["stops"]] == [1, 2]
    assert order("N-014").status == Order.Status.NEW


def test_driver_cannot_create_tour(driver_client, tomorrow):
    assert driver_client.post("/api/tours/", {"dispatch_date": tomorrow}).status_code == 403
