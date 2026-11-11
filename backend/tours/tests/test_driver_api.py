from datetime import timedelta

import pytest
from django.utils import timezone

from tours.models import Order, Stop, Tour
from tours.tests.conftest import client_for


@pytest.fixture
def started_tour(seeded):
    # Današnja tura voznika Vida, ki je že v dostavi
    return Tour.objects.get(dispatch_date=timezone.localdate(), status=Tour.Status.IN_DELIVERY)


@pytest.fixture
def luka_client(seeded):
    # Voznik Luka ima jutri potrjeno turo
    return client_for("voznik3@turaplan.si")


def luka_tour():
    return Tour.objects.get(driver__email="voznik3@turaplan.si", status=Tour.Status.CONFIRMED)


def mark(client, stop, result, reason=""):
    return client.post(f"/api/stops/{stop.id}/result/", {"result": result, "reason": reason})


def pending_stops(tour):
    return list(tour.stops.filter(result=Stop.Result.PENDING).order_by("sequence"))


def test_driver_sees_only_own_confirmed_tours(driver_client):
    tours = driver_client.get("/api/my-tours/").data
    assert {tour["driver"]["email"] for tour in tours} == {"voznik@turaplan.si"}
    assert Tour.Status.DRAFT not in {tour["status"] for tour in tours}


def test_driver_cannot_open_draft_or_other_drivers_tour(driver_client, started_tour):
    draft = Tour.objects.get(driver__email="voznik@turaplan.si", status=Tour.Status.DRAFT)
    assert driver_client.get(f"/api/tours/{started_tour.id}/").status_code == 200
    assert driver_client.get(f"/api/tours/{draft.id}/").status_code == 404
    assert driver_client.get(f"/api/tours/{luka_tour().id}/").status_code == 404


def test_tour_cannot_be_started_before_dispatch_date(luka_client):
    tour = luka_tour()
    response = luka_client.post(f"/api/tours/{tour.id}/start/")
    assert response.status_code == 400
    assert response.data == ["Turo je mogoče začeti najprej na datum odpreme"]
    assert luka_client.get(f"/api/tours/{tour.id}/").data["start_errors"] == response.data


def test_tour_is_started_on_dispatch_date(luka_client):
    tour = luka_tour()
    tour.dispatch_date = timezone.localdate()
    tour.save()
    response = luka_client.post(f"/api/tours/{tour.id}/start/")
    assert response.status_code == 200
    assert response.data["status"] == Tour.Status.IN_DELIVERY
    assert response.data["started_at"] is not None


def test_tour_cannot_be_started_while_other_tour_is_in_delivery(driver_client, started_tour):
    # Včerajšnja tura je še v dostavi, današnja je potrjena
    started_tour.dispatch_date = timezone.localdate() - timedelta(days=2)
    started_tour.save()
    tour = Tour.objects.get(driver__email="voznik@turaplan.si", status=Tour.Status.DRAFT)
    tour.dispatch_date = timezone.localdate()
    tour.status = Tour.Status.CONFIRMED
    tour.save()
    response = driver_client.post(f"/api/tours/{tour.id}/start/")
    assert response.status_code == 400
    assert response.data == ["Najprej zaključi turo, ki je že v dostavi"]


def test_delivered_stop_marks_order_delivered(driver_client, started_tour):
    stop = pending_stops(started_tour)[0]
    response = mark(driver_client, stop, "DELIVERED")
    assert response.status_code == 200
    stop.refresh_from_db()
    assert stop.result == Stop.Result.DELIVERED
    assert stop.marked_at is not None
    assert stop.order.status == Order.Status.DELIVERED


def test_not_delivered_requires_reason(driver_client, started_tour):
    response = mark(driver_client, pending_stops(started_tour)[0], "NOT_DELIVERED")
    assert response.status_code == 400
    assert response.data == ["Razlog nedostave je obvezen"]


def test_not_delivered_order_returns_to_unassigned(driver_client, dispatcher_client, started_tour):
    stop = pending_stops(started_tour)[0]
    mark(driver_client, stop, "NOT_DELIVERED", "Stranka zaprta")
    stop.refresh_from_db()
    assert stop.reason == "Stranka zaprta"
    assert stop.order.status == Order.Status.NOT_DELIVERED
    numbers = [order["number"] for order in dispatcher_client.get("/api/orders/").data]
    assert stop.order.number in numbers


def test_marking_last_stop_does_not_complete_tour(driver_client, started_tour):
    # Voznik turo zaključi sam, da lahko do takrat še popravi napačno oznako
    for stop in pending_stops(started_tour):
        response = mark(driver_client, stop, "DELIVERED")
    assert response.data["status"] == Tour.Status.IN_DELIVERY
    assert response.data["complete_errors"] == []


def test_driver_can_correct_mark_while_tour_is_in_delivery(driver_client, started_tour):
    stop = pending_stops(started_tour)[0]
    mark(driver_client, stop, "DELIVERED")
    response = mark(driver_client, stop, "NOT_DELIVERED", "Stranka zaprta")
    assert response.status_code == 200
    stop.refresh_from_db()
    assert stop.result == Stop.Result.NOT_DELIVERED
    assert stop.order.status == Order.Status.NOT_DELIVERED


def test_mark_cannot_be_changed_after_order_is_planned_again(driver_client, dispatcher_client, started_tour):
    stop = pending_stops(started_tour)[0]
    mark(driver_client, stop, "NOT_DELIVERED", "Stranka zaprta")
    # Disponent naročilo doda v jutrišnji osnutek
    draft = Tour.objects.get(status=Tour.Status.DRAFT)
    dispatcher_client.post(f"/api/tours/{draft.id}/stops/", {"order": stop.order.id})
    response = mark(driver_client, stop, "DELIVERED")
    assert response.status_code == 400
    assert response.data == ["Naročilo je že v novi turi, zato oznake ni mogoče spremeniti"]


def test_tour_with_unmarked_stops_cannot_be_completed(driver_client, started_tour):
    response = driver_client.post(f"/api/tours/{started_tour.id}/complete/")
    assert response.status_code == 400
    assert response.data == [f"Neoznačeni postanki: {len(pending_stops(started_tour))}"]


def test_completed_tour_cannot_be_changed(driver_client, started_tour):
    for stop in pending_stops(started_tour):
        mark(driver_client, stop, "DELIVERED")
    response = driver_client.post(f"/api/tours/{started_tour.id}/complete/")
    assert response.status_code == 200
    assert response.data["status"] == Tour.Status.COMPLETED
    assert response.data["completed_at"] is not None
    response = mark(driver_client, started_tour.stops.first(), "NOT_DELIVERED", "Napaka")
    assert response.status_code == 400
    assert response.data == ["Postanke je mogoče označiti samo v turi, ki je v dostavi"]


def test_driver_cannot_mark_other_drivers_stop(luka_client, started_tour):
    assert mark(luka_client, pending_stops(started_tour)[0], "DELIVERED").status_code == 404


def test_dispatcher_cannot_mark_stop_or_start_tour(dispatcher_client, started_tour):
    assert mark(dispatcher_client, pending_stops(started_tour)[0], "DELIVERED").status_code == 403
    assert dispatcher_client.post(f"/api/tours/{luka_tour().id}/start/").status_code == 403
